import json
import logging
from app.utils.agent_base import BaseAgent

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


class SearchStrategyAgent(BaseAgent):
    agent_name = "search_strategy"

    def generate_strategy(self, preferences: dict) -> dict:
        prompt = f"User preferences:\n{json.dumps(preferences, ensure_ascii=False, indent=2)}"
        return self._call_llm_json(
            system_prompt=SEARCH_STRATEGY_SYSTEM,
            user_prompt=prompt,
            fallback=FALLBACK_STRATEGY,
            temperature=0.3,
        )
