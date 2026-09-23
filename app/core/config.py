from functools import cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    ollama_host: str = "http://ollama:11434"
    model_name: str = "llama3.2:3b"
    sender_email: str = "routing-agent@example.com"

    #reads from .env file during local development
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()