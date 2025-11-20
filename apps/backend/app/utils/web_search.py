"""
Web Search Utility - Google Custom Search API
Perfect search results with Google's search quality and indexing
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
    Google Custom Search API for perfect search results
    - Uses Google's search quality and index
    - 100 FREE searches/day per API key
    - Best quality results for research
    """

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID", "")
        self.google_url = "https://www.googleapis.com/customsearch/v1"

    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_type: str = "web"
    ) -> List[Dict[str, Any]]:
        """
        Search using Google Custom Search API

        Args:
            query: Search query
            max_results: Maximum number of results (1-10 per request)
            search_type: Type of search (web, image, etc.)

        Returns:
            List of search results with title, url, snippet
        """
        if not self.google_api_key or not self.google_cse_id:
            logger.warning("Google API key or CSE ID not set, returning empty results")
            return []

        try:
            logger.info(f"Searching Google for: {query}")

            all_results = []
            # Google CSE allows max 10 results per request
            # To get more, need to paginate with 'start' parameter
            requests_needed = (max_results + 9) // 10  # Ceiling division

            for page in range(min(requests_needed, 3)):  # Max 3 pages (30 results)
                params = {
                    "key": self.google_api_key,
                    "cx": self.google_cse_id,
                    "q": query,
                    "num": min(10, max_results - len(all_results)),
                    "start": page * 10 + 1
                }

                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(
                        self.google_url,
                        params=params
                    )
                    response.raise_for_status()
                    data = response.json()

                # Extract search results
                items = data.get("items", [])

                for item in items:
                    all_results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google"
                    })

                # Break if we have enough results or no more pages
                if len(all_results) >= max_results or len(items) < 10:
                    break

            logger.info(f"Found {len(all_results)} results from Google Search")
            return all_results[:max_results]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("Google API quota exceeded (100/day limit)")
            else:
                logger.error(f"Google Search API error: {e.response.status_code}")
            return []

        except Exception as e:
            logger.error(f"Google Search failed: {e}")
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
            scraped = await self._scrape_url(url)

            if scraped:
                scraped_results.append({
                    **result,
                    "content": scraped.get("text", ""),
                    "html": scraped.get("html", ""),
                    "scraped": True
                })
            else:
                scraped_results.append({
                    **result,
                    "content": None,
                    "html": None,
                    "scraped": False
                })

        return scraped_results

    async def _scrape_url(self, url: str, timeout: int = 10) -> Optional[Dict[str, str]]:
        """
        Scrape URL and extract both HTML and clean text

        Args:
            url: URL to scrape
            timeout: Request timeout

        Returns:
            Dict with 'html' and 'text' or None
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Store raw HTML for contact extraction
                raw_html = response.text

                # Parse HTML
                soup = BeautifulSoup(raw_html, 'lxml')

                # Remove script and style elements for text extraction
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()

                # Get text
                text = soup.get_text()

                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)

                # Return both HTML and text
                return {
                    "html": raw_html[:20000],  # Keep more HTML for email extraction
                    "text": text[:5000]
                }

        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return None


# Global instance
web_searcher = WebSearcher()
