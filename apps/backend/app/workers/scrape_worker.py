"""
Scrape Worker - Processes web scraping jobs from Redis queue
Uses Playwright for headless browser scraping with politeness
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


class ScrapeWorker:
    """
    Web scraping worker
    - Pulls jobs from Redis scrape_queue
    - Performs scraping with Playwright/Puppeteer
    - Respects politeness delays
    - Sends completion webhooks
    """

    def __init__(self):
        self.queue_name = "scrape_queue"
        self.running = False

    async def start(self):
        """Start worker loop"""
        self.running = True
        logger.info("Scrape worker started")

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
                logger.error(f"Error in scrape worker: {e}")
                await asyncio.sleep(10)

    async def stop(self):
        """Stop worker"""
        self.running = False
        await redis_queue.close()
        logger.info("Scrape worker stopped")

    async def _process_job(self, job: dict):
        """
        Process a single scrape job

        Job format:
        {
            "url": "https://example.com",
            "task_id": "uuid",
            "user_id": "uuid",
            "timestamp": "ISO timestamp"
        }
        """
        url = job.get("url")
        task_id = job.get("task_id")
        user_id = job.get("user_id")

        logger.info(f"Processing scrape job for URL: {url}")

        try:
            # Perform scraping
            content = await self._scrape_url(url)

            # Store scrape result
            scrape_record = {
                "url": url,
                "content": content,
                "metadata": {
                    "task_id": task_id,
                    "user_id": user_id
                },
                "status": "completed",
                "created_at": datetime.utcnow().isoformat()
            }

            result = supabase_client.table("scrapes").insert(scrape_record).execute()
            scrape_id = result.data[0]["id"]

            # Send completion webhook
            await self._send_webhook({
                "event_type": "completed",
                "scrape_id": scrape_id,
                "url": url,
                "content": content,
                "metadata": {
                    "task_id": task_id,
                    "user_id": user_id
                }
            })

            logger.info(f"Scrape completed for {url}, scrape_id: {scrape_id}")

        except Exception as e:
            logger.error(f"Scrape failed for {url}: {e}")

            # Store failed scrape
            scrape_record = {
                "url": url,
                "content": None,
                "metadata": {
                    "task_id": task_id,
                    "user_id": user_id,
                    "error": str(e)
                },
                "status": "failed",
                "created_at": datetime.utcnow().isoformat()
            }

            supabase_client.table("scrapes").insert(scrape_record).execute()

            # Send failure webhook
            await self._send_webhook({
                "event_type": "failed",
                "url": url,
                "error": str(e),
                "metadata": {
                    "task_id": task_id,
                    "user_id": user_id
                }
            })

    async def _scrape_url(self, url: str) -> str:
        """
        Scrape URL using Playwright/Puppeteer

        For production: Use Playwright or Puppeteer
        For now: Simple HTTP fetch as placeholder

        Args:
            url: URL to scrape

        Returns:
            Scraped content (HTML or text)
        """
        # TODO: In production, replace with Playwright
        # from playwright.async_api import async_playwright
        # async with async_playwright() as p:
        #     browser = await p.chromium.launch()
        #     page = await browser.new_page()
        #     await page.goto(url)
        #     content = await page.content()
        #     await browser.close()
        #     return content

        # Placeholder: Simple HTTP fetch
        try:
            async with httpx.AsyncClient(timeout=settings.SCRAPE_TIMEOUT) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                return response.text

        except Exception as e:
            logger.error(f"HTTP fetch failed for {url}: {e}")
            raise

    async def _send_webhook(self, payload: dict):
        """
        Send webhook to orchestrator

        Args:
            payload: Webhook payload
        """
        import json

        webhook_url = f"{settings.BACKEND_URL}/webhook/scrape"
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
scrape_worker = ScrapeWorker()


# Standalone script entry point
async def main():
    """Run scrape worker as standalone process"""
    worker = ScrapeWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Shutting down scrape worker...")
        await worker.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
