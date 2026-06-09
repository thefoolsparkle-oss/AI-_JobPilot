from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        temperature: float | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        agent_name: str = "",
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def achat(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        temperature: float | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        agent_name: str = "",
    ) -> str:
        raise NotImplementedError

    def chat_with_reasoning(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        temperature: float | None = None,
        agent_name: str = "",
    ) -> str:
        return self.chat(messages=messages, response_format=response_format, temperature=temperature, agent_name=agent_name)

    async def achat_with_reasoning(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        temperature: float | None = None,
        agent_name: str = "",
    ) -> str:
        return await self.achat(messages=messages, response_format=response_format, temperature=temperature, agent_name=agent_name)
