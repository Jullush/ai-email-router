"""Application settings loaded from environment variables."""
from functools import cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """App configuration; each field can be overridden by an env var of the same name (e.g. SMTP_HOST).

    Defaults use Docker Compose service hostnames.
    """
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    ollama_host: str = "http://ollama:11434"
    model_name: str = "llama3.2:3b"
    sender_email: str = "routing-agent@example.com"
    llm_timeout: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@cache
def get_settings() -> Settings:
    """Return the cached Settings instance."""
    return Settings()

settings = get_settings()