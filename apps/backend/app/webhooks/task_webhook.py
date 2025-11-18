"""
Task Webhook - Receives task completion notifications from workers
Verifies HMAC signature and processes task updates
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


@router.post("/webhook/task")
async def task_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None)
):
    """
    Task webhook for completion notifications

    Security: HMAC SHA256 signature verification

    Payload format:
    {
        "event_type": "completed" | "failed" | "progress",
        "task_id": "uuid",
        "agent_name": "product_manager",
        "output": {},
        "error": "error message if failed",
        "progress": 0-100
    }
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify HMAC signature
    if not verify_webhook_signature(body, x_webhook_signature):
        logger.warning("Invalid webhook signature for task webhook")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("event_type")
    task_id = payload.get("task_id")
    agent_name = payload.get("agent_name")

    logger.info(f"Task webhook received: {event_type} for task {task_id}")

    # Store webhook event
    webhook_record = {
        "source": "worker",
        "event_type": event_type,
        "payload": payload,
        "processed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    supabase_client.table("webhook_events").insert(webhook_record).execute()

    # Process based on event type
    if event_type == "completed":
        await _handle_task_completed(payload)

    elif event_type == "failed":
        await _handle_task_failed(payload)

    elif event_type == "progress":
        await _handle_task_progress(payload)

    return {"status": "ok", "event_type": event_type}


async def _handle_task_completed(payload: dict):
    """Handle task completion"""
    task_id = payload.get("task_id")
    output = payload.get("output", {})
    agent_name = payload.get("agent_name")

    # Update task status
    supabase_client.table("agent_tasks") \
        .update({
            "status": "completed",
            "output": output,
            "completed_at": datetime.utcnow().isoformat()
        }) \
        .eq("id", task_id) \
        .execute()

    logger.info(f"Task {task_id} ({agent_name}) marked as completed")

    # Create alert for user
    task_result = supabase_client.table("agent_tasks") \
        .select("user_id") \
        .eq("id", task_id) \
        .single() \
        .execute()

    if task_result.data:
        user_id = task_result.data["user_id"]

        alert_record = {
            "user_id": user_id,
            "type": "task_completed",
            "message": f"{agent_name.replace('_', ' ').title()} task completed",
            "metadata": {
                "task_id": task_id,
                "agent_name": agent_name
            }
        }

        supabase_client.table("alerts").insert(alert_record).execute()


async def _handle_task_failed(payload: dict):
    """Handle task failure"""
    task_id = payload.get("task_id")
    error = payload.get("error", "Unknown error")
    agent_name = payload.get("agent_name")

    # Update task status
    supabase_client.table("agent_tasks") \
        .update({
            "status": "failed",
            "error": error,
            "completed_at": datetime.utcnow().isoformat()
        }) \
        .eq("id", task_id) \
        .execute()

    logger.error(f"Task {task_id} ({agent_name}) failed: {error}")

    # Create alert for user
    task_result = supabase_client.table("agent_tasks") \
        .select("user_id") \
        .eq("id", task_id) \
        .single() \
        .execute()

    if task_result.data:
        user_id = task_result.data["user_id"]

        alert_record = {
            "user_id": user_id,
            "type": "task_failed",
            "message": f"{agent_name.replace('_', ' ').title()} task failed",
            "metadata": {
                "task_id": task_id,
                "agent_name": agent_name,
                "error": error
            }
        }

        supabase_client.table("alerts").insert(alert_record).execute()


async def _handle_task_progress(payload: dict):
    """Handle task progress update"""
    task_id = payload.get("task_id")
    progress = payload.get("progress", 0)

    # Update task metadata with progress
    task_result = supabase_client.table("agent_tasks") \
        .select("metadata") \
        .eq("id", task_id) \
        .single() \
        .execute()

    current_metadata = task_result.data.get("metadata", {}) if task_result.data else {}
    current_metadata["progress"] = progress

    supabase_client.table("agent_tasks") \
        .update({"metadata": current_metadata}) \
        .eq("id", task_id) \
        .execute()

    logger.info(f"Task {task_id} progress: {progress}%")
