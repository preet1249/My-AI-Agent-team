"""
Lead Generation Scraper Agent - Finds leads via web scraping with politeness
Uses Puppeteer/Playwright for scraping + LLM for analysis
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.utils.openrouter_client import openrouter_client
from app.database import supabase_client
from app.utils.security import generate_external_id
from app.utils.contact_extractor import contact_extractor
from app.utils.web_search import web_searcher
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
        target_urls: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        criteria: Optional[Dict[str, Any]] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process lead generation request

        Args:
            user_id: User UUID
            target_urls: List of URLs to scrape (optional)
            search_query: DuckDuckGo search query to find leads (optional)
            criteria: Lead scoring criteria (industry, size, etc.)
            external_id: Optional idempotency key

        Returns:
            Dict with REAL leads (emails, names, phones, company info)
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
            urls_to_scrape = []

            # If search_query provided, use DuckDuckGo to find URLs
            if search_query:
                logger.info(f"Searching DuckDuckGo for: {search_query}")
                search_results = await web_searcher.search_and_scrape(
                    query=search_query,
                    max_results=10,
                    scrape_content=True
                )
                urls_to_scrape = [r['url'] for r in search_results if r.get('scraped')]

                # Also include search results content for analysis
                for result in search_results:
                    if result.get('scraped'):
                        # Extract contacts from scraped HTML (use html for better extraction)
                        html_content = result.get('html') or result.get('content', '')
                        contacts = contact_extractor.extract_all_contacts(
                            html=html_content,
                            url=result['url']
                        )

                        # Create leads from extracted contacts
                        leads.extend(await self._create_leads_from_contacts(
                            user_id=user_id,
                            contacts=contacts,
                            task_id=task_id,
                            criteria=criteria
                        ))
            elif target_urls:
                urls_to_scrape = target_urls
            else:
                raise ValueError("Either target_urls or search_query must be provided")

            # Process any remaining URLs
            for url in urls_to_scrape:
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

    async def _create_leads_from_contacts(
        self,
        user_id: str,
        contacts: Dict[str, Any],
        task_id: str,
        criteria: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create lead records from extracted contact data

        Args:
            user_id: User UUID
            contacts: Extracted contact data from contact_extractor
            task_id: Agent task ID
            criteria: Lead scoring criteria

        Returns:
            List of created lead records
        """
        leads = []
        company_info = contacts.get('company_info', {})
        company_name = company_info.get('company', 'Unknown Company')

        # Extract primary email (first one found)
        emails = contacts.get('emails', [])
        primary_email = emails[0] if emails else None

        # If we have emails, create individual leads
        if emails:
            for email in emails[:5]:  # Limit to top 5 emails per page
                # Try to match email with team member
                matching_member = None
                email_prefix = email.split('@')[0].lower()

                for member in contacts.get('team_members', []):
                    member_name = member.get('name', '').lower()
                    if any(part in email_prefix for part in member_name.split()):
                        matching_member = member
                        break

                # Score lead based on criteria
                score = await self._score_lead(
                    email=email,
                    company_info=company_info,
                    role=matching_member.get('role') if matching_member else None,
                    criteria=criteria
                )

                lead_record = {
                    "user_id": user_id,
                    "email": email,
                    "name": matching_member.get('name') if matching_member else None,
                    "company": company_name,
                    "score": score,
                    "metadata": {
                        "source_url": contacts.get('source_url'),
                        "task_id": task_id,
                        "phone": contacts.get('phones', [])[0] if contacts.get('phones') else None,
                        "linkedin": matching_member.get('linkedin') if matching_member else None,
                        "role": matching_member.get('role') if matching_member else None,
                        "company_description": company_info.get('description'),
                        "company_keywords": company_info.get('keywords', []),
                        "company_social": company_info.get('social', {}),
                        "extraction_timestamp": datetime.utcnow().isoformat()
                    },
                    "status": "new"
                }

                try:
                    result = supabase_client.table("leads").insert(lead_record).execute()
                    leads.append(result.data[0])
                    logger.info(f"Created lead: {email} from {company_name}")
                except Exception as e:
                    logger.error(f"Failed to create lead for {email}: {e}")

        # If no emails but we have team members with LinkedIn, create leads
        elif contacts.get('team_members'):
            for member in contacts.get('team_members', [])[:3]:  # Top 3 members
                linkedin_url = None
                # Check if member name appears in LinkedIn profiles
                for profile in contacts.get('linkedin_profiles', []):
                    member_name_parts = member.get('name', '').lower().split()
                    if any(part in profile.lower() for part in member_name_parts):
                        linkedin_url = profile
                        break

                score = await self._score_lead(
                    email=None,
                    company_info=company_info,
                    role=member.get('role'),
                    criteria=criteria
                )

                lead_record = {
                    "user_id": user_id,
                    "email": None,  # No email found
                    "name": member.get('name'),
                    "company": company_name,
                    "score": score,
                    "metadata": {
                        "source_url": contacts.get('source_url'),
                        "task_id": task_id,
                        "linkedin": linkedin_url,
                        "role": member.get('role'),
                        "company_description": company_info.get('description'),
                        "company_keywords": company_info.get('keywords', []),
                        "needs_email_enrichment": True
                    },
                    "status": "needs_enrichment"
                }

                try:
                    result = supabase_client.table("leads").insert(lead_record).execute()
                    leads.append(result.data[0])
                    logger.info(f"Created lead (no email): {member.get('name')} from {company_name}")
                except Exception as e:
                    logger.error(f"Failed to create lead for {member.get('name')}: {e}")

        return leads

    async def _score_lead(
        self,
        email: Optional[str],
        company_info: Dict[str, Any],
        role: Optional[str],
        criteria: Optional[Dict[str, Any]]
    ) -> int:
        """
        Score a lead based on available data and criteria

        Returns:
            Score from 0-100
        """
        score = 50  # Base score

        # Email presence
        if email:
            score += 10
            # Corporate email (not gmail/yahoo/etc)
            if email and not any(domain in email.lower() for domain in ['gmail', 'yahoo', 'hotmail', 'outlook']):
                score += 10

        # Role scoring
        if role:
            role_lower = role.lower()
            if any(title in role_lower for title in ['ceo', 'founder', 'president', 'chief']):
                score += 15
            elif any(title in role_lower for title in ['vp', 'director', 'head']):
                score += 10
            elif any(title in role_lower for title in ['manager', 'lead']):
                score += 5

        # Company info quality
        if company_info.get('description'):
            score += 5
        if company_info.get('social', {}).get('linkedin'):
            score += 5

        # Criteria matching
        if criteria:
            keywords = company_info.get('keywords', [])
            target_keywords = criteria.get('keywords', [])

            if target_keywords:
                matches = sum(1 for kw in target_keywords if kw.lower() in [k.lower() for k in keywords])
                score += min(matches * 5, 20)  # Up to 20 points for keyword matches

        return min(score, 100)  # Cap at 100


# Global instance
leadgen_scraper_agent = LeadGenScraperAgent()
