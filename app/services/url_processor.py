import asyncio
import httpx
import logging
from typing import List, Dict, Optional
from functools import lru_cache
from lxml import html
import redis.asyncio as redis
import htmldate

from app.core.config import settings


class URLProcessor:
    def __init__(
        self,
        timeout: int = settings.URL_PROCESSOR_TIMEOUT,
        max_concurrent: int = settings.MAX_CONCURRENT_REQUESTS,
        cache_ttl: int = 3600,
    ):
        self.timeout = httpx.Timeout(
            connect=5.0, read=timeout, write=timeout, pool=timeout
        )
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            limits=httpx.Limits(
                max_connections=max_concurrent,
                max_keepalive_connections=max_concurrent // 2,
                keepalive_expiry=30.0,
            ),
        )

        self.redis_client = redis.Redis(
            host=settings.REDIS_CLOUD_HOST,
            port=settings.REDIS_CLOUD_PORT,
            username="default",
            password=settings.REDIS_CLOUD_PASSWORD,
            decode_responses=True,
        )

        self.cache_ttl = cache_ttl
        self.logger = logging.getLogger(__name__)
        self.max_retries = 3
        self.base_delay = 1

    @lru_cache(maxsize=1000)
    def _get_cached_date(self, url: str) -> Optional[str]:
        return None

    async def _get_redis_cache(self, url: str) -> Optional[str]:
        try:
            return await self.redis_client.get(f"url_date:{url}")
        except Exception as e:
            self.logger.error(f"Redis error for {url}: {e}")
            return None

    async def _set_redis_cache(self, url: str, date: str):
        try:
            await self.redis_client.set(f"url_date:{url}", date, ex=self.cache_ttl)
        except Exception as e:
            self.logger.error(f"Redis cache set error for {url}: {e}")

    def _parse_html_date(
        self, html_content: str, original_date: Optional[str] = None
    ) -> Optional[str]:
        try:
            return htmldate.find_date(
                html_content,
                original_date=original_date,
                verbose=False,
                outputformat="%d %b %Y",
            )
        except Exception as e:
            self.logger.error(f"HTML date parsing error: {e}")
            return None

    async def _fetch_with_retry(self, url: str, headers: dict) -> httpx.Response:
        for attempt in range(self.max_retries):
            try:
                return await self.http_client.get(url, headers=headers)
            except Exception as _:
                if attempt == self.max_retries - 1:
                    raise
                delay = self.base_delay * (2**attempt)
                await asyncio.sleep(delay)

    async def extract_last_updated(self, url: str) -> Dict:
        try:
            if not url or not url.startswith(("http://", "https://")):
                return {"url": url, "last_updated": None, "error": "Invalid URL format"}

            cached_date = self._get_cached_date(url)
            if cached_date:
                return {"url": url, "last_updated": cached_date}

            redis_cached_date = await self._get_redis_cache(url)
            if redis_cached_date:
                return {"url": url, "last_updated": redis_cached_date}

            async with self.semaphore:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Encoding": "gzip, deflate",
                }

                response = await self._fetch_with_retry(url, headers)
                content = await response.aread()
                tree = html.fromstring(content)
                body = tree.find(".//body")
                body_content = html.tostring(
                    body if body is not None else tree
                ).decode()

                last_updated = self._parse_html_date(
                    body_content, response.headers.get("Last-Modified")
                )

                if last_updated:
                    self._get_cached_date.cache_info()
                    await self._set_redis_cache(url, last_updated)

                return {
                    "url": url,
                    "last_updated": last_updated,
                }

        except Exception as e:
            self.logger.error(f"Error processing {url}: {e}")
            return {"url": url, "last_updated": None, "error": str(e)}

    async def process_urls(self, urls: List[str]) -> List[Dict]:
        domain_groups = {}
        for url in urls:
            try:
                domain = httpx.URL(url).host
                domain_groups.setdefault(domain, []).append(url)
            except Exception:
                continue

        all_results = []
        for domain, domain_urls in domain_groups.items():
            tasks = []
            for url in domain_urls:
                if tasks:
                    await asyncio.sleep(0.1)
                tasks.append(self.extract_last_updated(url))

            domain_results = await asyncio.gather(*tasks, return_exceptions=True)
            all_results.extend(domain_results)

        return all_results

    async def cleanup(self):
        await self.http_client.aclose()
        await self.redis_client.close()
