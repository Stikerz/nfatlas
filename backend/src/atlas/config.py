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

    # --- Draw / entropy (Week 6) ------------------------------------------
    # Founder decision 2026-07-27 §0.1: hybrid — stub in tests+CI, live in
    # demo dev. Production must be 'live' (validated below).
    draw_entropy_mode: Literal["stub", "live"] = "stub"
    # Drand mainnet group public key — persisted for V1 client-side BLS
    # verify. Optional today (V0.5 trusts drand's HTTPS endpoint).
    drand_group_public_key: str | None = None

    # --- Server-seed encryption at rest (Week 8, ADR-006 §Stage 1) --------
    # Fernet key: 32 url-safe base64 bytes (44-char string).
    # Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # Rotation: annual + on-incident per ADR-006 §Trade-offs. Multi-key
    # rotation (with a `key_version` column) is a W9+ story.
    server_seed_key: SecretStr = Field(
        description="Fernet key for encrypting draws.server_seed_encrypted at rest.",
        min_length=44,
        max_length=44,
    )

    # --- Demo mode (Week 7) -----------------------------------------------
    # Founder decision 2026-07-29 §0.3: when true, seed_v0_5.py compresses
    # the seeded draw's close/draw times to now+10min / now+11min so the
    # pitch doesn't wait days. Production must be false (validated).
    demo_mode: bool = False

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
            if self.draw_entropy_mode == "stub":
                raise ValueError(
                    "ATLAS_DRAW_ENTROPY_MODE must be 'live' in production "
                    "(V0.5 stub for demo-offline runs only)."
                )
            if self.demo_mode:
                raise ValueError(
                    "ATLAS_DEMO_MODE must be false in production "
                    "(V0.5 demo-timing shortcut only)."
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
