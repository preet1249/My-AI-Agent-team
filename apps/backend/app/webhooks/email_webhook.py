"""
Email Webhook - Receives Gmail push notifications for incoming emails
Verifies HMAC signature and processes email events
"""
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from datetime import datetime
from app.utils.security import verify_webhook_signature
from app.database import supabase_client
from app.agents.outbound_emailer import outbound_emailer_agent
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook/email")
async def email_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None)
):
    """
    Gmail webhook for incoming emails and delivery events

    Security: HMAC SHA256 signature verification

    Payload format:
    {
        "event_type": "received" | "delivered" | "opened" | "clicked" | "replied" | "bounced",
        "email_id": "message_id",
        "lead_id": "uuid",
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Email subject",
        "body": "Email body text",
        "metadata": {}
    }
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify HMAC signature
    if not verify_webhook_signature(body, x_webhook_signature):
        logger.warning("Invalid webhook signature for email webhook")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("event_type")
    lead_id = payload.get("lead_id")
    email_id = payload.get("email_id")

    logger.info(f"Email webhook received: {event_type} for lead {lead_id}")

    # Store webhook event
    webhook_record = {
        "source": "gmail",
        "event_type": event_type,
        "payload": payload,
        "processed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    supabase_client.table("webhook_events").insert(webhook_record).execute()

    # Process based on event type
    if event_type == "received":
        await _handle_email_received(payload)

    elif event_type == "replied":
        await _handle_email_replied(payload)

    elif event_type in ["delivered", "opened", "clicked"]:
        await _handle_email_engagement(payload)

    elif event_type == "bounced":
        await _handle_email_bounced(payload)

    return {"status": "ok", "event_type": event_type}


async def _handle_email_received(payload: dict):
    """Handle incoming email"""
    from_email = payload.get("from")
    subject = payload.get("subject")
    body = payload.get("body")

    # Find or create lead
    lead_result = supabase_client.table("leads") \
        .select("*") \
        .eq("email", from_email) \
        .execute()

    if lead_result.data:
        lead_id = lead_result.data[0]["id"]
        user_id = lead_result.data[0]["user_id"]
    else:
        # Create new lead
        new_lead = {
            "email": from_email,
            "status": "new",
            "metadata": {"first_contact_subject": subject}
        }
        lead_insert = supabase_client.table("leads").insert(new_lead).execute()
        lead_id = lead_insert.data[0]["id"]
        user_id = lead_insert.data[0]["user_id"]

    # Record email event
    event_record = {
        "user_id": user_id,
        "lead_id": lead_id,
        "event_type": "received",
        "metadata": {
            "subject": subject,
            "body_preview": body[:200] if body else ""
        }
    }
    supabase_client.table("email_events").insert(event_record).execute()

    # Update lead history
    history_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "email_received",
        "subject": subject
    }

    lead = lead_result.data[0] if lead_result.data else {}
    current_history = lead.get("history", [])
    current_history.append(history_entry)

    supabase_client.table("leads") \
        .update({"history": current_history}) \
        .eq("id", lead_id) \
        .execute()

    logger.info(f"Processed received email from {from_email}")


async def _handle_email_replied(payload: dict):
    """Handle email reply from lead"""
    lead_id = payload.get("lead_id")
    reply_text = payload.get("body")

    # Get lead
    lead_result = supabase_client.table("leads") \
        .select("*") \
        .eq("id", lead_id) \
        .single() \
        .execute()

    lead = lead_result.data
    user_id = lead["user_id"]

    # Increase lead score (engagement signal)
    new_score = min(lead.get("score", 0) + 10, 100)

    # Update lead status to engaged
    supabase_client.table("leads") \
        .update({
            "score": new_score,
            "status": "engaged"
        }) \
        .eq("id", lead_id) \
        .execute()

    # Record email event
    event_record = {
        "user_id": user_id,
        "lead_id": lead_id,
        "event_type": "replied",
        "metadata": {
            "reply_preview": reply_text[:200] if reply_text else ""
        }
    }
    supabase_client.table("email_events").insert(event_record).execute()

    logger.info(f"Processed email reply for lead {lead_id}, score increased to {new_score}")


async def _handle_email_engagement(payload: dict):
    """Handle email engagement events (delivered, opened, clicked)"""
    lead_id = payload.get("lead_id")
    event_type = payload.get("event_type")

    # Get lead
    lead_result = supabase_client.table("leads") \
        .select("*") \
        .eq("id", lead_id) \
        .single() \
        .execute()

    lead = lead_result.data
    user_id = lead["user_id"]

    # Score increases based on engagement
    score_increase = {
        "delivered": 0,
        "opened": 5,
        "clicked": 15
    }.get(event_type, 0)

    new_score = min(lead.get("score", 0) + score_increase, 100)

    supabase_client.table("leads") \
        .update({"score": new_score}) \
        .eq("id", lead_id) \
        .execute()

    # Record email event
    event_record = {
        "user_id": user_id,
        "lead_id": lead_id,
        "event_type": event_type,
        "metadata": payload.get("metadata", {})
    }
    supabase_client.table("email_events").insert(event_record).execute()

    logger.info(f"Processed {event_type} event for lead {lead_id}, score: {new_score}")


async def _handle_email_bounced(payload: dict):
    """Handle bounced emails"""
    lead_id = payload.get("lead_id")

    # Get lead
    lead_result = supabase_client.table("leads") \
        .select("*") \
        .eq("id", lead_id) \
        .single() \
        .execute()

    lead = lead_result.data
    user_id = lead["user_id"]

    # Mark lead as bounced
    supabase_client.table("leads") \
        .update({"status": "bounced"}) \
        .eq("id", lead_id) \
        .execute()

    # Record email event
    event_record = {
        "user_id": user_id,
        "lead_id": lead_id,
        "event_type": "bounced",
        "metadata": payload.get("metadata", {})
    }
    supabase_client.table("email_events").insert(event_record).execute()

    logger.info(f"Processed bounced email for lead {lead_id}")
