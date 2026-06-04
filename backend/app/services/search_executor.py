import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SearchExecutor:
    async def search_jobs(self, query: str, max_results: int = 10) -> list[dict]:
        """Execute a search and return job-related results."""
        try:
            from ddgs import DDGS
        except ImportError:
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                return [{"error": "ddgs/duckduckgo_search not installed", "title": "", "url": "", "snippet": ""}]

        jobs = []
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{query} site:zhipin.com OR site:nowcoder.com OR site:shixiseng.com", max_results=max_results))
                for r in results:
                    jobs.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "")[:300],
                        "source": "duckduckgo",
                    })
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed for '{query}': {e}")
            return [{"error": str(e), "title": "", "url": "", "snippet": ""}]

        return jobs

    async def execute_search_strategy(self, queries: list[str], max_per_query: int = 5) -> list[dict]:
        """Run multiple search queries and return deduplicated results."""
        seen_urls = set()
        all_jobs = []
        for query in queries[:5]:
            results = await self.search_jobs(query, max_per_query)
            for r in results:
                if r.get("url") and r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    all_jobs.append(r)
        return all_jobs[:30]
