"""Application configuration — the ONLY module in the codebase that reads env vars.

Per ADR-012 §Application-code conventions:
  - Every secret/config value is declared here as a typed Pydantic field.
  - `SecretStr` is used for credentials.
  - A startup self-check (called from `atlas.main`) verifies required fields
    are present and shape-correct; missing/malformed values fail-fast on boot.
  - CI enforces via grep that no other module calls `os.environ` / `os.getenv`.

Naming: env vars are UPPER_SNAKE_CASE; the same identifier used here as a
lowercase attribute. Prefix `ATLAS_` avoids collisions on the container host.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ATLAS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    env: Literal["dev", "test", "staging", "production"] = "dev"

    # --- Database ---------------------------------------------------------
    database_url: SecretStr = Field(
        description="Async SQLAlchemy URL: postgresql+asyncpg://user:pass@host:5432/db",
    )

    # --- HTTP -------------------------------------------------------------
    http_host: str = "0.0.0.0"  # noqa: S104 — container-scoped bind, not host-network
    http_port: int = 8000

    # --- Placeholders for later Week 3 days -------------------------------
    # (Day 2+ will populate real values; declared here so config.py stays the
    # single source of truth from Day 1.)
    jwt_signing_key: SecretStr | None = None
    otp_pepper: SecretStr | None = None

    # --- Placeholders for later weeks -------------------------------------
    paystack_secret_key: SecretStr | None = None
    bvn_pepper: SecretStr | None = None  # ADR-010: never rotated
    sentry_dsn: SecretStr | None = None

    def is_production(self) -> bool:
        return self.env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings instance. Reload requires process restart (ADR-012)."""
    return Settings()  # type: ignore[call-arg]
