"""
Scrape Webhook - Receives scrape job completion notifications
Verifies HMAC signature and processes scrape results
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


@router.post("/webhook/scrape")
async def scrape_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None)
):
    """
    Scrape webhook for job completion

    Security: HMAC SHA256 signature verification

    Payload format:
    {
        "event_type": "completed" | "failed",
        "scrape_id": "uuid",
        "url": "https://example.com",
        "content": "scraped HTML/text",
        "metadata": {},
        "error": "error message if failed"
    }
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify HMAC signature
    if not verify_webhook_signature(body, x_webhook_signature):
        logger.warning("Invalid webhook signature for scrape webhook")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("event_type")
    url = payload.get("url")
    scrape_id = payload.get("scrape_id")

    logger.info(f"Scrape webhook received: {event_type} for URL {url}")

    # Store webhook event
    webhook_record = {
        "source": "scraper",
        "event_type": event_type,
        "payload": payload,
        "processed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    supabase_client.table("webhook_events").insert(webhook_record).execute()

    # Process based on event type
    if event_type == "completed":
        await _handle_scrape_completed(payload)

    elif event_type == "failed":
        await _handle_scrape_failed(payload)

    return {"status": "ok", "event_type": event_type}


async def _handle_scrape_completed(payload: dict):
    """Handle successful scrape completion"""
    url = payload.get("url")
    content = payload.get("content")
    metadata = payload.get("metadata", {})

    # Store scrape result with cache TTL
    scrape_record = {
        "url": url,
        "content": content,
        "metadata": metadata,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat()
    }

    result = supabase_client.table("scrapes").insert(scrape_record).execute()
    scrape_id = result.data[0]["id"]

    logger.info(f"Stored scrape result for {url}, scrape_id: {scrape_id}")

    # If this was part of a lead generation task, update task
    task_id = metadata.get("task_id")
    if task_id:
        # Find the task and update with scrape results
        task_result = supabase_client.table("agent_tasks") \
            .select("*") \
            .eq("id", task_id) \
            .single() \
            .execute()

        if task_result.data:
            task = task_result.data
            output = task.get("output", {})
            output["scrape_completed"] = True
            output["scrape_id"] = scrape_id

            supabase_client.table("agent_tasks") \
                .update({"output": output}) \
                .eq("id", task_id) \
                .execute()


async def _handle_scrape_failed(payload: dict):
    """Handle failed scrape"""
    url = payload.get("url")
    error = payload.get("error", "Unknown error")
    metadata = payload.get("metadata", {})

    # Store failed scrape
    scrape_record = {
        "url": url,
        "content": None,
        "metadata": {
            **metadata,
            "error": error
        },
        "status": "failed",
        "created_at": datetime.utcnow().isoformat()
    }

    supabase_client.table("scrapes").insert(scrape_record).execute()

    # Check if we should add domain to backoff
    domain = _extract_domain(url)
    await _add_domain_backoff(domain, hours=1)

    logger.warning(f"Scrape failed for {url}: {error}")


def _extract_domain(url: str) -> str:
    """Extract domain from URL"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc


async def _add_domain_backoff(domain: str, hours: int = 1):
    """Add domain to backoff list"""
    backoff_until = datetime.utcnow() + timedelta(hours=hours)

    backoff_record = {
        "domain": domain,
        "backoff_until": backoff_until.isoformat(),
        "reason": "scrape_failure"
    }

    supabase_client.table("domain_backoff").insert(backoff_record).execute()

    logger.info(f"Added domain {domain} to backoff until {backoff_until}")


from datetime import timedelta
