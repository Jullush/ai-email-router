"""Application settings loaded from environment variables."""
from functools import cache
from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration; each field can be overridden by an env var of the same name
    (e.g. SMTP_HOST) or by a `.env` file in the working directory.

    Defaults use Docker Compose service hostnames. `llm_timeout` is in seconds.
    """
    smtp_host: str = "mailhog"
    smtp_port: int = Field(default=1025, ge=1, le=65535)
    ollama_host: str = "http://ollama:11434"
    model_name: str = "llama3.2:3b"
    sender_email: EmailStr = "routing-agent@example.com"
    llm_timeout: float = Field(default=60.0, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@cache
def get_settings() -> Settings:
    """Return the cached Settings instance."""
    return Settings()

settings = get_settings()