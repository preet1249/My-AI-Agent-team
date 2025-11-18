"""
Calendar Webhook - Receives calendar update notifications
Verifies HMAC signature and processes calendar events
"""
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from datetime import datetime
from app.utils.security import verify_webhook_signature
from app.database import supabase_client
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook/calendar")
async def calendar_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None)
):
    """
    Calendar webhook for event updates

    Security: HMAC SHA256 signature verification

    Payload format:
    {
        "event_type": "created" | "updated" | "cancelled" | "reminder",
        "calendar_event_id": "uuid",
        "user_id": "uuid",
        "title": "Event title",
        "start_time": "ISO timestamp",
        "metadata": {}
    }
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify HMAC signature
    if not verify_webhook_signature(body, x_webhook_signature):
        logger.warning("Invalid webhook signature for calendar webhook")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("event_type")
    calendar_event_id = payload.get("calendar_event_id")
    user_id = payload.get("user_id")

    logger.info(f"Calendar webhook received: {event_type} for event {calendar_event_id}")

    # Store webhook event
    webhook_record = {
        "source": "calendar",
        "event_type": event_type,
        "payload": payload,
        "processed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    supabase_client.table("webhook_events").insert(webhook_record).execute()

    # Process based on event type
    if event_type == "created":
        await _handle_event_created(payload)

    elif event_type == "updated":
        await _handle_event_updated(payload)

    elif event_type == "cancelled":
        await _handle_event_cancelled(payload)

    elif event_type == "reminder":
        await _handle_event_reminder(payload)

    return {"status": "ok", "event_type": event_type}


async def _handle_event_created(payload: dict):
    """Handle calendar event creation"""
    user_id = payload.get("user_id")
    title = payload.get("title")
    start_time = payload.get("start_time")

    # Update calendar event in database
    event_record = {
        "user_id": user_id,
        "title": title,
        "start_time": start_time,
        "duration_minutes": payload.get("duration_minutes", 30),
        "metadata": payload.get("metadata", {})
    }

    result = supabase_client.table("calendar_events").insert(event_record).execute()

    logger.info(f"Created calendar event: {title} for user {user_id}")


async def _handle_event_updated(payload: dict):
    """Handle calendar event update"""
    calendar_event_id = payload.get("calendar_event_id")

    # Update event
    update_data = {}
    if "title" in payload:
        update_data["title"] = payload["title"]
    if "start_time" in payload:
        update_data["start_time"] = payload["start_time"]

    if update_data:
        supabase_client.table("calendar_events") \
            .update(update_data) \
            .eq("id", calendar_event_id) \
            .execute()

    logger.info(f"Updated calendar event {calendar_event_id}")


async def _handle_event_cancelled(payload: dict):
    """Handle calendar event cancellation"""
    calendar_event_id = payload.get("calendar_event_id")

    # Mark as cancelled
    supabase_client.table("calendar_events") \
        .update({"metadata": {"status": "cancelled"}}) \
        .eq("id", calendar_event_id) \
        .execute()

    logger.info(f"Cancelled calendar event {calendar_event_id}")


async def _handle_event_reminder(payload: dict):
    """Handle calendar event reminder"""
    calendar_event_id = payload.get("calendar_event_id")
    user_id = payload.get("user_id")

    # Create alert for upcoming event
    event_result = supabase_client.table("calendar_events") \
        .select("*") \
        .eq("id", calendar_event_id) \
        .single() \
        .execute()

    event = event_result.data

    alert_record = {
        "user_id": user_id,
        "type": "calendar_reminder",
        "message": f"Upcoming: {event['title']} in 15 minutes",
        "metadata": {"calendar_event_id": calendar_event_id}
    }

    supabase_client.table("alerts").insert(alert_record).execute()

    logger.info(f"Created reminder alert for event {calendar_event_id}")
