"""otps + sessions (Day 3)

Revision ID: 0002_otps_and_sessions
Revises: 0001_users_audit_log
Create Date: 2026-07-15 09:00

Adds:
  - otps table with issued/expires/consumed timestamps, code_hash (HMAC-SHA-256
    keyed on ATLAS_OTP_PEPPER; the plaintext code is only ever in-memory and
    in the Mailhog SMTP body), channel enum, purpose enum, resend_count.
  - Partial index on active (unconsumed) OTPs per user + purpose for the
    rate-limit and dedupe queries in atlas.identity.otp_service.
  - sessions table with JWT-parallel expires_at + revoked_at, IP + UA capture
    per session.created audit event (ADR-005 payload spec).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002_otps_and_sessions"
down_revision: Union[str, None] = "0001_users_audit_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # One statement per op.execute — asyncpg cannot prepare multi-stmt SQL.
    op.execute(
        """
        CREATE TABLE otps (
            id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id      UUID NOT NULL REFERENCES users(id),
            code_hash    TEXT NOT NULL,
            channel      TEXT NOT NULL,
            purpose      TEXT NOT NULL,
            issued_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
            expires_at   TIMESTAMPTZ NOT NULL,
            consumed_at  TIMESTAMPTZ,
            resend_count INTEGER NOT NULL DEFAULT 0,
            CONSTRAINT ck_otps_channel_enum CHECK (channel IN ('mailhog', 'sms')),
            CONSTRAINT ck_otps_purpose_enum CHECK (purpose IN ('registration', 'login_mfa'))
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_otps_user_purpose_active "
        "ON otps (user_id, purpose) WHERE consumed_at IS NULL;"
    )
    op.execute("CREATE INDEX ix_otps_issued_at ON otps (issued_at);")

    op.execute(
        """
        CREATE TABLE sessions (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id     UUID NOT NULL REFERENCES users(id),
            issued_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
            expires_at  TIMESTAMPTZ NOT NULL,
            revoked_at  TIMESTAMPTZ,
            ip_addr     INET,
            user_agent  TEXT
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_sessions_user_active "
        "ON sessions (user_id) WHERE revoked_at IS NULL;"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS sessions;")
    op.execute("DROP TABLE IF EXISTS otps;")
