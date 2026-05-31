from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_FAST_MODEL: str = "deepseek-chat"
    DEEPSEEK_REASONING_MODEL: str = "deepseek-reasoner"

    DATABASE_URL: str = "sqlite:///./jobpilot.db"

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_RETRIES: int = 2

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
