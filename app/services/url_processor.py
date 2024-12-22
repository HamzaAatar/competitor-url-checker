import asyncio
import httpx
import htmldate
import logging
from typing import List, Dict
from bs4 import BeautifulSoup

from app.core.config import settings


class URLProcessor:
    def __init__(
        self,
        timeout: int = settings.URL_PROCESSOR_TIMEOUT,
        max_concurrent: int = settings.MAX_CONCURRENT_REQUESTS,
    ):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=self.max_concurrent),
        )
        self.logger = logging.getLogger(__name__)

    async def extract_last_updated(self, url: str) -> Dict:
        try:
            if not url or not url.startswith(("http://", "https://")):
                return {"url": url, "last_updated": None, "error": "Invalid URL format"}

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = await self.http_client.get(url, headers=headers)

            # Parse HTML and extract body content
            soup = BeautifulSoup(response.text, "html.parser")
            body_content = str(soup.body) if soup.body else response.text

            last_updated = htmldate.find_date(
                body_content,
                original_date=response.headers.get("Last-Modified"),
                verbose=False,
                outputformat="%d %b %Y",
            )

            return {
                "url": url,
                "last_updated": last_updated,
            }
        except Exception as e:
            self.logger.error(f"Error processing {url}: {e}")
            return {"url": url, "last_updated": None, "error": str(e)}

    async def process_urls(self, urls: List[str]) -> List[Dict]:
        tasks = [self.extract_last_updated(url) for url in urls]
        return await asyncio.gather(*tasks)
