
from app.llm.provider import LLMProvider

_llm_instance: LLMProvider | None = None


def get_llm() -> LLMProvider:
    global _llm_instance
    if _llm_instance is None:
        from app.llm.deepseek_provider import DeepSeekProvider
        _llm_instance = DeepSeekProvider()
    return _llm_instance


def reset_llm():
    global _llm_instance
    _llm_instance = None
