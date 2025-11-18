"""
Lead Generation Scraper Agent - Finds leads via web scraping with politeness
Uses Puppeteer/Playwright for scraping + LLM for analysis
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.utils.openrouter_client import openrouter_client
from app.database import supabase_client
from app.utils.security import generate_external_id
from app.redis_client import redis_queue
import asyncio
import logging

logger = logging.getLogger(__name__)


class LeadGenScraperAgent:
    """
    Lead Generation Scraper AI Agent
    - Scrapes websites for lead data
    - Respects politeness delays (2-5s)
    - Caches scrape results (24h TTL)
    - Scores leads based on criteria
    """

    def __init__(self):
        self.agent_name = "leadgen_scraper"
        self.client = openrouter_client
        self.scrape_delay = (2, 5)  # 2-5 seconds between requests
        self.cache_ttl = 86400  # 24 hours

    async def process(
        self,
        user_id: str,
        target_urls: List[str],
        criteria: Optional[Dict[str, Any]] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process lead generation request

        Args:
            user_id: User UUID
            target_urls: List of URLs to scrape
            criteria: Lead scoring criteria (industry, size, etc.)
            external_id: Optional idempotency key

        Returns:
            Dict with leads found and scores
        """
        external_id = external_id or generate_external_id("scrape")

        # Check for duplicate request
        existing = supabase_client.table("agent_tasks") \
            .select("*") \
            .eq("external_id", external_id) \
            .execute()

        if existing.data:
            logger.info(f"Returning cached result for external_id: {external_id}")
            return existing.data[0]["output"]

        # Create task record
        task = {
            "user_id": user_id,
            "agent_name": self.agent_name,
            "input": {"target_urls": target_urls, "criteria": criteria},
            "status": "processing",
            "external_id": external_id,
            "created_at": datetime.utcnow().isoformat()
        }

        task_result = supabase_client.table("agent_tasks").insert(task).execute()
        task_id = task_result.data[0]["id"]

        try:
            leads = []

            for url in target_urls:
                # Check domain backoff
                domain = self._extract_domain(url)
                if await self._is_domain_blocked(domain):
                    logger.warning(f"Domain {domain} is temporarily blocked due to backoff")
                    continue

                # Check cache first
                cached_scrape = await self._get_cached_scrape(url)
                if cached_scrape:
                    logger.info(f"Using cached scrape for {url}")
                    scrape_data = cached_scrape
                else:
                    # Enqueue scrape job (worker will handle actual scraping)
                    scrape_job = {
                        "url": url,
                        "task_id": task_id,
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await redis_queue.enqueue("scrape_queue", scrape_job)

                    # For now, return pending status
                    # In production, worker will update task when complete
                    logger.info(f"Enqueued scrape job for {url}")
                    scrape_data = {"status": "pending", "url": url}

                # Analyze scrape data with LLM
                if scrape_data.get("content"):
                    lead_info = await self._extract_lead_info(scrape_data["content"], criteria)
                    if lead_info:
                        # Store lead
                        lead_record = {
                            "user_id": user_id,
                            "email": lead_info.get("email"),
                            "company": lead_info.get("company"),
                            "score": lead_info.get("score", 0),
                            "metadata": {
                                "source_url": url,
                                "criteria_match": lead_info.get("criteria_match", {}),
                                "task_id": task_id
                            },
                            "status": "new"
                        }
                        result = supabase_client.table("leads").insert(lead_record).execute()
                        leads.append(result.data[0])

                # Politeness delay
                delay = asyncio.uniform(*self.scrape_delay)
                await asyncio.sleep(delay)

            # Update task as completed
            output = {
                "leads_found": len(leads),
                "leads": leads,
                "timestamp": datetime.utcnow().isoformat()
            }

            supabase_client.table("agent_tasks") \
                .update({"status": "completed", "output": output}) \
                .eq("id", task_id) \
                .execute()

            logger.info(f"Lead Gen Scraper task {task_id} completed. Found {len(leads)} leads")
            return output

        except Exception as e:
            logger.error(f"Lead Gen Scraper task {task_id} failed: {e}")

            supabase_client.table("agent_tasks") \
                .update({
                    "status": "failed",
                    "error": str(e)
                }) \
                .eq("id", task_id) \
                .execute()

            raise

    async def _get_cached_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Check if URL has been scraped recently"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.cache_ttl)

        result = supabase_client.table("scrapes") \
            .select("*") \
            .eq("url", url) \
            .gte("created_at", cutoff.isoformat()) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if result.data:
            return result.data[0]
        return None

    async def _is_domain_blocked(self, domain: str) -> bool:
        """Check if domain is in backoff period"""
        result = supabase_client.table("domain_backoff") \
            .select("*") \
            .eq("domain", domain) \
            .gte("backoff_until", datetime.utcnow().isoformat()) \
            .execute()

        return len(result.data) > 0

    async def _extract_lead_info(
        self,
        content: str,
        criteria: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract lead information from scraped content using LLM

        Args:
            content: Scraped webpage content
            criteria: Lead scoring criteria

        Returns:
            Lead info dict or None
        """
        prompt = f"""
        Analyze this webpage content and extract lead information:

        Content: {content[:2000]}

        Extract:
        1. Company name
        2. Email addresses
        3. Industry
        4. Company size indicators

        Criteria for scoring: {criteria}

        Return JSON with: company, email, industry, score (0-100)
        """

        try:
            response = await self.client.call_model(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )

            # Parse JSON from response
            import json
            lead_data = json.loads(response["content"])
            return lead_data

        except Exception as e:
            logger.error(f"Failed to extract lead info: {e}")
            return None

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc


# Global instance
leadgen_scraper_agent = LeadGenScraperAgent()
