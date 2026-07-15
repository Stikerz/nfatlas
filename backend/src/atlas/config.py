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

from pydantic import Field, SecretStr, model_validator
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

    # --- Identity secrets (required from Day 3) ---------------------------
    jwt_signing_key: SecretStr = Field(
        description="HS256 signing key for session JWTs (ADR-012 rotation 90d).",
        min_length=32,
    )
    otp_pepper: SecretStr = Field(
        description="HMAC-SHA-256 pepper for OTP code hashing.",
        min_length=32,
    )
    session_ttl_hours: int = 8  # founder decision 2026-07-13

    # --- Dev-only OTP delivery (Mailhog SMTP stub for real SMS) -----------
    mailhog_host: str = "mailhog"
    mailhog_port: int = 1025

    # --- Wallet (V0.5) ----------------------------------------------------
    # Founder decision 2026-07-15 §0.4: lets Week 4 tests exercise
    # record_ticket_purchase against a placeholder draw_id before the ticket
    # module lands Week 5. Production must set this to false.
    wallet_allow_stub_draw: bool = True

    @model_validator(mode="after")
    def _prod_safety(self) -> "Settings":
        if self.env == "production" and self.wallet_allow_stub_draw:
            raise ValueError(
                "ATLAS_WALLET_ALLOW_STUB_DRAW must be false in production "
                "(V0.5 stub for the pre-ticket-module weeks only)."
            )
        return self

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
