import logging
from typing import Any, Optional
from openai import OpenAI

from app.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self._aclient: Optional[Any] = None
        self.default_model = model
        self.default_temperature = 0.2

    def _get_aclient(self):
        if self._aclient is None:
            from openai import AsyncOpenAI
            self._aclient = AsyncOpenAI(api_key=self.client.api_key, base_url=str(self.client.base_url))
        return self._aclient

    def _build_kwargs(
        self,
        model: Optional[str],
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
        }
        if response_format is not None:
            kwargs["response_format"] = response_format
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        return kwargs

    def chat(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        agent_name: str = "",
    ) -> str:
        kwargs = self._build_kwargs(model, messages, response_format, temperature, max_tokens)
        try:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.warning(f"OpenAI chat failed: {e}")
            raise

    async def achat(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        agent_name: str = "",
    ) -> str:
        kwargs = self._build_kwargs(model, messages, response_format, temperature, max_tokens)
        try:
            response = await self._get_aclient().chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.warning(f"OpenAI async chat failed: {e}")
            raise


class GenericOpenAIProvider(OpenAIProvider):
    """For API-compatible providers (Kimi, Qwen, etc.)"""
    pass
