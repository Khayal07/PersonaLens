"""Mərkəzi konfiqurasiya — bütün dəyərlər environment-dən gəlir.

Model adı yalnız burada (OPENROUTER_MODEL) idarə olunur ki, free-tier
modeli dəyişmək üçün kodu deyil, yalnız `.env`-i redaktə etmək kifayət etsin.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # OpenRouter
    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-oss-20b:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # LLM çağırış parametrləri
    llm_timeout_seconds: float = 60.0
    llm_max_retries: int = 4
    llm_temperature: float = 0.7

    # PostgreSQL
    postgres_user: str = "personalens"
    postgres_password: str = "personalens"
    postgres_db: str = "personalens"
    postgres_host: str = "db"
    postgres_port: int = 5432

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
