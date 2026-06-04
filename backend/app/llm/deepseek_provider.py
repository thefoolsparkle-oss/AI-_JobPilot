import json
import time
import logging
from typing import Any, Optional

from openai import OpenAI, AsyncOpenAI

from app.core.config import settings
from app.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    if settings.DEEPSEEK_API_KEY:
        return settings.DEEPSEEK_API_KEY
    from app.services.settings_service import get_settings_store
    return get_settings_store().get_key()


def _get_models():
    from app.services.settings_service import get_settings_store
    return get_settings_store().get_models()


class DeepSeekProvider(LLMProvider):
    def __init__(self):
        api_key = _get_api_key()
        models = _get_models()
        self.client = OpenAI(
            api_key=api_key,
            base_url=models["base_url"],
        )
        self._aclient: Optional[AsyncOpenAI] = None
        self.fast_model = models["fast_model"]
        self.reasoning_model = models["reasoning_model"]
        self.default_temperature = settings.LLM_TEMPERATURE
        self.max_retries = settings.LLM_MAX_RETRIES

    def _get_aclient(self) -> AsyncOpenAI:
        if self._aclient is None:
            models = _get_models()
            self._aclient = AsyncOpenAI(
                api_key=_get_api_key(),
                base_url=models["base_url"],
            )
        return self._aclient

    def _build_kwargs(
        self,
        model: str,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]],
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
        }
        if response_format is not None:
            kwargs["response_format"] = response_format
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        return kwargs

    def _retry_chat(self, kwargs: dict[str, Any], agent_name: str = "") -> str:
        last_error: Optional[Exception] = None
        t0 = time.time()
        model = kwargs.get("model", "")
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(**kwargs)
                self._log_call(model, agent_name, response, time.time() - t0)
                return response.choices[0].message.content or ""
            except Exception as e:
                last_error = e
                logger.warning(f"DeepSeek chat attempt {attempt + 1} failed: {e}")
        raise last_error or RuntimeError("DeepSeek chat failed")

    def _log_call(self, model: str, agent_name: str, response, duration_s: float):
        try:
            from app.services.agent_logger import AgentLogger
            log = AgentLogger(agent_name or "unknown")
            usage = response.usage
            log.log_llm_call(
                model=model,
                prompt_tokens=usage.prompt_tokens if usage else None,
                completion_tokens=usage.completion_tokens if usage else None,
                duration_ms=int(duration_s * 1000),
            )
        except Exception:
            pass

    async def _retry_achat(self, kwargs: dict[str, Any]) -> str:
        last_error: Optional[Exception] = None
        aclient = self._get_aclient()
        for attempt in range(self.max_retries + 1):
            try:
                response = await aclient.chat.completions.create(**kwargs)
                return response.choices[0].message.content or ""
            except Exception as e:
                last_error = e
                logger.warning(f"DeepSeek async chat attempt {attempt + 1} failed: {e}")
        raise last_error or RuntimeError("DeepSeek async chat failed")

    def chat(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        agent_name: str = "",
    ) -> str:
        kwargs = self._build_kwargs(
            model=model or self.fast_model,
            messages=messages,
            response_format=response_format,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return self._retry_chat(kwargs, agent_name)

    async def achat(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        agent_name: str = "",
    ) -> str:
        kwargs = self._build_kwargs(
            model=model or self.fast_model,
            messages=messages,
            response_format=response_format,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return await self._retry_achat(kwargs)

    def chat_with_reasoning(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
        agent_name: str = "",
    ) -> str:
        return self.chat(
            messages=messages,
            response_format=response_format,
            temperature=temperature,
            model=self.reasoning_model,
            agent_name=agent_name,
        )

    async def achat_with_reasoning(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
    ) -> str:
        return await self.achat(
            messages=messages,
            response_format=response_format,
            temperature=temperature,
            model=self.reasoning_model,
        )
