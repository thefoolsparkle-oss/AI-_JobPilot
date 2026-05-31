from typing import Any, Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def achat(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        raise NotImplementedError

    def chat_with_reasoning(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Default: fallback to normal chat. Override for providers with reasoning models."""
        return self.chat(messages=messages, response_format=response_format, temperature=temperature)

    async def achat_with_reasoning(
        self,
        messages: list[dict[str, str]],
        response_format: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Default: fallback to normal async chat."""
        return await self.achat(messages=messages, response_format=response_format, temperature=temperature)
