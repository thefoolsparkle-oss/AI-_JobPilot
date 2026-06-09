import logging

from app.utils.json_utils import extract_json

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents with shared LLM call and JSON extraction logic."""

    agent_name: str = "base"

    def __init__(self):
        from app.llm.factory import get_llm
        self.llm = get_llm()

    def _call_llm(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        return self.llm.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            agent_name=self.agent_name,
            **kwargs,
        )

    def _call_llm_json(self, system_prompt: str, user_prompt: str, fallback: dict, **kwargs) -> dict:
        try:
            response = self._call_llm(system_prompt, user_prompt, **kwargs)
            return extract_json(response) or fallback
        except Exception as e:
            logger.warning(f"{self.agent_name} failed: {e}")
            return dict(fallback)

    def _call_llm_with_reasoning(self, system_prompt: str, user_prompt: str, fallback: dict = None) -> dict:
        try:
            response = self.llm.chat_with_reasoning(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                agent_name=self.agent_name,
            )
            return extract_json(response) or (fallback or {})
        except Exception as e:
            logger.warning(f"{self.agent_name} reasoning failed: {e}")
            return dict(fallback) if fallback else {}
