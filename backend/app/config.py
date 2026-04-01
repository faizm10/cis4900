from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/cs_learning"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Tutor: openai | anthropic | gemini
    LLM_PROVIDER: Literal["openai", "anthropic", "gemini"] = Field(
        default="anthropic",
        validation_alias=AliasChoices("LLM_PROVIDER"),
    )

    # OpenAI-compatible (LLM_PROVIDER=openai)
    LLM_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LLM_API_KEY", "OPENAI_API_KEY"),
    )
    LLM_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("LLM_BASE_URL", "OPENAI_BASE_URL"),
    )
    LLM_MODEL: str = Field(
        default="gpt-4o-mini",
        validation_alias=AliasChoices("LLM_MODEL", "OPENAI_MODEL"),
    )

    # Anthropic (LLM_PROVIDER=anthropic)
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    ANTHROPIC_API_URL: str = "https://api.anthropic.com"
    ANTHROPIC_VERSION: str = "2023-06-01"

    # Gemini (LLM_PROVIDER=gemini)
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_API_BASE_URL: str = "https://generativelanguage.googleapis.com"

    LLM_TIMEOUT_SEC: float = Field(
        default=60.0,
        validation_alias=AliasChoices("LLM_TIMEOUT_SEC"),
    )


settings = Settings()
