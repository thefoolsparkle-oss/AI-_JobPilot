import json
import logging
from app.llm import DeepSeekProvider

logger = logging.getLogger(__name__)

SEARCH_STRATEGY_SYSTEM = """You are a job search strategist. Based on the user's preferences, generate effective search queries and filters.

Output valid JSON:
{
  "queries": ["搜索词1", "搜索词2", "搜索词3"],
  "negative_keywords": ["排除词1", "排除词2"],
  "preferred_sources": ["公司官网", "校招官网", "实习平台"]
}

Rules:
- Generate 5-8 specific, actionable search queries in Chinese.
- Include variations: different role names, different platforms.
- negative_keywords: roles and terms to exclude (e.g., 销售, 全职, 社招).
- preferred_sources: where to search.
"""

FALLBACK_STRATEGY = {"queries": [], "negative_keywords": [], "preferred_sources": []}


class SearchStrategyAgent:
    def __init__(self):
        self.llm = DeepSeekProvider()

    def generate_strategy(self, preferences: dict) -> dict:
        try:
            prompt = f"User preferences:\n{json.dumps(preferences, ensure_ascii=False, indent=2)}"
            response = self.llm.chat(
                messages=[
                    {"role": "system", "content": SEARCH_STRATEGY_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                agent_name="search_strategy",
            )
            if "```json" in response:
                start = response.index("```json") + 7
                end = response.index("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.index("```") + 3
                end = response.index("```", start)
                response = response[start:end].strip()
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Search strategy failed: {e}")
            return dict(FALLBACK_STRATEGY)
