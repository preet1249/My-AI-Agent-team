"""
Email Worker - Processes email sending jobs from Redis queue
Uses Gmail API for sending emails
"""
import asyncio
import httpx
from datetime import datetime
from typing import Optional
from app.redis_client import redis_queue
from app.database import supabase_client
from app.utils.security import create_webhook_signature
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailWorker:
    """
    Email sending worker
    - Pulls jobs from Redis email_queue
    - Sends emails via Gmail API
    - Tracks delivery status
    - Sends completion webhooks
    """

    def __init__(self):
        self.queue_name = "email_queue"
        self.running = False

    async def start(self):
        """Start worker loop"""
        self.running = True
        logger.info("Email worker started")

        await redis_queue.connect()

        while self.running:
            try:
                # Dequeue job (blocking with timeout)
                job = await redis_queue.dequeue(self.queue_name, timeout=30)

                if job:
                    await self._process_job(job)
                else:
                    # No jobs, wait a bit
                    await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error in email worker: {e}")
                await asyncio.sleep(10)

    async def stop(self):
        """Stop worker"""
        self.running = False
        await redis_queue.close()
        logger.info("Email worker stopped")

    async def _process_job(self, job: dict):
        """
        Process a single email job

        Job format:
        {
            "lead_id": "uuid",
            "to_email": "recipient@example.com",
            "subject": "Email subject",
            "body": "Email body",
            "campaign_id": "uuid",
            "task_id": "uuid",
            "user_id": "uuid",
            "timestamp": "ISO timestamp"
        }
        """
        lead_id = job.get("lead_id")
        to_email = job.get("to_email")
        subject = job.get("subject")
        body = job.get("body")
        campaign_id = job.get("campaign_id")
        task_id = job.get("task_id")
        user_id = job.get("user_id")

        logger.info(f"Processing email job for {to_email}")

        try:
            # Send email via Gmail API
            message_id = await self._send_email(to_email, subject, body)

            # Record email event as sent
            event_record = {
                "user_id": user_id,
                "lead_id": lead_id,
                "event_type": "sent",
                "metadata": {
                    "campaign_id": campaign_id,
                    "task_id": task_id,
                    "message_id": message_id,
                    "subject": subject
                }
            }

            supabase_client.table("email_events").insert(event_record).execute()

            # Update lead history
            lead_result = supabase_client.table("leads") \
                .select("history") \
                .eq("id", lead_id) \
                .single() \
                .execute()

            history = lead_result.data.get("history", []) if lead_result.data else []
            history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "email_sent",
                "subject": subject,
                "message_id": message_id
            })

            supabase_client.table("leads") \
                .update({"history": history}) \
                .eq("id", lead_id) \
                .execute()

            # Send completion webhook
            await self._send_webhook({
                "event_type": "sent",
                "lead_id": lead_id,
                "to_email": to_email,
                "message_id": message_id,
                "metadata": {
                    "campaign_id": campaign_id,
                    "task_id": task_id
                }
            })

            logger.info(f"Email sent to {to_email}, message_id: {message_id}")

        except Exception as e:
            logger.error(f"Email send failed for {to_email}: {e}")

            # Record failed email event
            event_record = {
                "user_id": user_id,
                "lead_id": lead_id,
                "event_type": "failed",
                "metadata": {
                    "campaign_id": campaign_id,
                    "task_id": task_id,
                    "error": str(e)
                }
            }

            supabase_client.table("email_events").insert(event_record).execute()

            # Send failure webhook
            await self._send_webhook({
                "event_type": "failed",
                "lead_id": lead_id,
                "to_email": to_email,
                "error": str(e),
                "metadata": {
                    "campaign_id": campaign_id,
                    "task_id": task_id
                }
            })

    async def _send_email(self, to_email: str, subject: str, body: str) -> str:
        """
        Send email via Gmail API

        For production: Use Gmail API with OAuth2
        For now: Placeholder

        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body

        Returns:
            Message ID
        """
        # TODO: In production, replace with Gmail API
        # from googleapiclient.discovery import build
        # from google.oauth2.credentials import Credentials
        #
        # creds = Credentials.from_authorized_user_info(...)
        # service = build('gmail', 'v1', credentials=creds)
        #
        # message = MIMEText(body)
        # message['to'] = to_email
        # message['subject'] = subject
        # raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        #
        # result = service.users().messages().send(
        #     userId='me',
        #     body={'raw': raw}
        # ).execute()
        #
        # return result['id']

        # Placeholder: Log and return fake message ID
        logger.info(f"[PLACEHOLDER] Sending email to {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body[:100]}...")

        # Generate fake message ID
        import uuid
        message_id = str(uuid.uuid4())

        return message_id

    async def _send_webhook(self, payload: dict):
        """
        Send webhook to orchestrator

        Args:
            payload: Webhook payload
        """
        import json

        webhook_url = f"{settings.BACKEND_URL}/webhook/email"
        payload_json = json.dumps(payload).encode('utf-8')

        # Create HMAC signature
        signature = create_webhook_signature(payload_json)

        headers = {
            "Content-Type": "application/json",
            "x-webhook-signature": signature
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    webhook_url,
                    content=payload_json,
                    headers=headers
                )
                response.raise_for_status()
                logger.info(f"Webhook sent successfully to {webhook_url}")

        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")


# Global instance
email_worker = EmailWorker()


# Standalone script entry point
async def main():
    """Run email worker as standalone process"""
    worker = EmailWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Shutting down email worker...")
        await worker.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
