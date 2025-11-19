"""
Web Search Utility - FREE DuckDuckGo Search (No API Key Required)
Automatically finds and scrapes relevant websites/blogs
"""
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
import httpx
from bs4 import BeautifulSoup
import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

logger = logging.getLogger(__name__)


class WebSearcher:
    """
    FREE web search using DuckDuckGo
    - No API key required
    - Unlimited searches
    - Returns clean, structured results
    - Automatic retry with exponential backoff
    """

    def __init__(self):
        # Don't store DDGS instance - create fresh ones to avoid rate limits
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        retry=retry_if_exception(lambda e: "Ratelimit" in str(e))
    )
    async def search(
        self,
        query: str,
        max_results: int = 10,
        region: str = "wt-wt"
    ) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo and return results with automatic retry on rate limits

        Args:
            query: Search query
            max_results: Maximum number of results
            region: Region code (wt-wt = worldwide)

        Returns:
            List of search results with title, url, snippet
        """
        try:
            logger.info(f"Searching DuckDuckGo for: {query}")

            # Add small delay to avoid rate limits
            await asyncio.sleep(1)

            # Create fresh DDGS instance for each search
            ddgs = DDGS(timeout=20)

            results = ddgs.text(
                keywords=query,
                region=region,
                max_results=max_results
            )

            formatted_results = []
            for r in results:
                formatted_results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source": "duckduckgo"
                })

            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            # If rate limited, log and retry (tenacity will handle)
            if "Ratelimit" in str(e):
                logger.warning(f"DuckDuckGo rate limit hit, retrying with backoff...")
                raise  # Re-raise to trigger retry

            logger.error(f"DuckDuckGo search failed: {e}")
            return []

    async def search_and_scrape(
        self,
        query: str,
        max_results: int = 5,
        scrape_content: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo and optionally scrape each result

        Args:
            query: Search query
            max_results: How many results to scrape
            scrape_content: Whether to scrape full content

        Returns:
            List of results with full scraped content
        """
        # Get search results
        results = await self.search(query, max_results=max_results)

        if not scrape_content:
            return results

        # Scrape each URL
        scraped_results = []
        for result in results:
            url = result["url"]
            content = await self._scrape_url(url)

            scraped_results.append({
                **result,
                "content": content,
                "scraped": content is not None
            })

        return scraped_results

    async def _scrape_url(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Scrape URL and extract clean text

        Args:
            url: URL to scrape
            timeout: Request timeout

        Returns:
            Cleaned text content or None
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Parse HTML
                soup = BeautifulSoup(response.text, 'lxml')

                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()

                # Get text
                text = soup.get_text()

                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)

                # Limit to first 5000 chars to save tokens
                return text[:5000]

        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return None


# Global instance
web_searcher = WebSearcher()
