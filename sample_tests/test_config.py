"""Tests for application settings."""
import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_env_vars_override_defaults_and_are_validated(monkeypatch):
    """Env vars override defaults, are type-coerced, and invalid values are rejected."""
    monkeypatch.setenv("SMTP_PORT", "2525")
    monkeypatch.setenv("LLM_TIMEOUT", "12.5")

    settings = Settings(_env_file=None)  #ignore any local .env

    assert settings.smtp_port == 2525
    assert settings.llm_timeout == 12.5
    assert settings.smtp_host == "mailhog"

    monkeypatch.setenv("SMTP_PORT", "70000")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
