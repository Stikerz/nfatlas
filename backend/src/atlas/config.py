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
    http_host: str = "0.0.0.0"
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

    # --- Payment / Paystack (V0.5 Week 4) ---------------------------------
    # Founder decision 2026-07-15 §0.1: Paystack fully stubbed for Week 4.
    # `paystack_stub_mode = true` short-circuits the adapter to fixture
    # responses. Production must set this to false (validated below).
    # `paystack_secret_key` + `paystack_public_key` are optional in stub
    # mode; required when stub_mode is off.
    # `paystack_webhook_secret` is required always — Day 4 exercises the
    # real HMAC-SHA-512 path even with the API side stubbed.
    paystack_stub_mode: bool = True
    paystack_secret_key: SecretStr | None = None
    paystack_public_key: str | None = None
    paystack_webhook_secret: SecretStr = Field(
        description="HMAC-SHA-512 secret for x-paystack-signature verification.",
        min_length=16,
    )

    @model_validator(mode="after")
    def _prod_safety(self) -> Settings:
        if self.env == "production":
            if self.wallet_allow_stub_draw:
                raise ValueError(
                    "ATLAS_WALLET_ALLOW_STUB_DRAW must be false in production "
                    "(V0.5 stub for the pre-ticket-module weeks only)."
                )
            if self.paystack_stub_mode:
                raise ValueError(
                    "ATLAS_PAYSTACK_STUB_MODE must be false in production "
                    "(V0.5 stub for the pre-live-sandbox weeks only)."
                )
            if self.paystack_secret_key is None or self.paystack_public_key is None:
                raise ValueError(
                    "ATLAS_PAYSTACK_SECRET_KEY and ATLAS_PAYSTACK_PUBLIC_KEY "
                    "are required when stub mode is off."
                )
        if not self.paystack_stub_mode and self.paystack_secret_key is None:
            raise ValueError(
                "ATLAS_PAYSTACK_SECRET_KEY is required when stub mode is off."
            )
        return self

    # --- Placeholders for later weeks -------------------------------------
    bvn_pepper: SecretStr | None = None  # ADR-010: never rotated
    sentry_dsn: SecretStr | None = None

    def is_production(self) -> bool:
        return self.env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings instance. Reload requires process restart (ADR-012)."""
    return Settings()
