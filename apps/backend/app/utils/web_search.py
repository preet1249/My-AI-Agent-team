"""
Web Search Utility - Brave Search API (FREE 2000 requests/month)
No rate limiting, official API, better than DuckDuckGo scraping
"""
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
import logging
import os
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WebSearcher:
    """
    FREE web search using Brave Search API
    - 2000 FREE requests/month (no credit card)
    - No rate limiting
    - Official API - won't get blocked
    - Better results than DuckDuckGo
    """

    def __init__(self):
        self.brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY", "")
        self.brave_url = "https://api.search.brave.com/res/v1/web/search"

    async def search(
        self,
        query: str,
        max_results: int = 10,
        country: str = "US"
    ) -> List[Dict[str, Any]]:
        """
        Search using Brave Search API (FREE 2000 requests/month)

        Args:
            query: Search query
            max_results: Maximum number of results (1-20)
            country: Country code (US, UK, etc.)

        Returns:
            List of search results with title, url, snippet
        """
        if not self.brave_api_key:
            logger.warning("Brave Search API key not set, returning empty results")
            return []

        try:
            logger.info(f"Searching Brave Search for: {query}")

            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }

            params = {
                "q": query,
                "count": min(max_results, 20),  # Max 20 per request
                "country": country,
                "search_lang": "en",
                "safesearch": "moderate"
            }

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    self.brave_url,
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()

            # Extract web results
            web_results = data.get("web", {}).get("results", [])

            formatted_results = []
            for r in web_results:
                formatted_results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("description", ""),
                    "source": "brave"
                })

            logger.info(f"Found {len(formatted_results)} results from Brave Search")
            return formatted_results

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("Brave Search rate limit hit (2000/month exceeded)")
            else:
                logger.error(f"Brave Search API error: {e.response.status_code}")
            return []

        except Exception as e:
            logger.error(f"Brave Search failed: {e}")
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
