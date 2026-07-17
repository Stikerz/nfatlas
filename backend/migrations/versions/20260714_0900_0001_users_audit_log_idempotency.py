"""users + audit_log + idempotency_records (Day 2)

Revision ID: 0001_users_audit_log
Revises:
Create Date: 2026-07-14 09:00

Implements:
  - ADR-005 audit_log with append-only enforcement via revoked
    UPDATE/DELETE grants + a chain-linkage trigger on INSERT. Full
    row_hash recomputation inside PL/pgSQL is deferred to the nightly
    verification job (see ADR-005 §Verification) — implementing JCS
    canonicalization in PL/pgSQL is impractical.
  - ADR-004 idempotency_records with a per-endpoint composite retention.
  - Identity users table with server-side 18+ check and Nigerian MSISDN
    format check.

Prerequisites installed: citext (case-insensitive email), pgcrypto
(gen_random_uuid).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_users_audit_log"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # ── users ────────────────────────────────────────────────────────────
    op.execute(
        """
        CREATE TABLE users (
            id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email          CITEXT NOT NULL,
            phone_e164     TEXT NOT NULL,
            password_hash  TEXT,
            date_of_birth  DATE NOT NULL,
            status         TEXT NOT NULL,
            created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_users_email UNIQUE (email),
            CONSTRAINT uq_users_phone_e164 UNIQUE (phone_e164),
            CONSTRAINT ck_users_date_of_birth_18_or_over
                CHECK (date_of_birth <= (CURRENT_DATE - INTERVAL '18 years')),
            CONSTRAINT ck_users_phone_e164_nigerian_msisdn
                CHECK (phone_e164 ~ '^\\+234[789]\\d{9}$'),
            CONSTRAINT ck_users_status_enum
                CHECK (status IN ('pending_verification', 'active', 'closed'))
        );
        """
    )

    # ── audit_log ────────────────────────────────────────────────────────
    op.execute(
        """
        CREATE TABLE audit_log (
            seq          BIGSERIAL PRIMARY KEY,
            occurred_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            actor_type   TEXT NOT NULL,
            actor_id     TEXT,
            event_name   TEXT NOT NULL,
            subject_type TEXT NOT NULL,
            subject_id   TEXT NOT NULL,
            payload      JSONB NOT NULL,
            prev_hash    TEXT NOT NULL,
            row_hash     TEXT NOT NULL,
            CONSTRAINT uq_audit_log_row_hash UNIQUE (row_hash)
        );
        """
    )

    # Chain-linkage trigger: on INSERT, verify NEW.prev_hash matches the
    # row_hash of the row immediately preceding by seq (or 'GENESIS' for
    # the first row). Full canonical-form re-hashing is done by the
    # nightly verification job per ADR-005 §Verification.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION audit_log_verify_chain()
        RETURNS TRIGGER AS $$
        DECLARE
            prev_row_hash TEXT;
        BEGIN
            SELECT row_hash INTO prev_row_hash
            FROM audit_log
            WHERE seq < NEW.seq
            ORDER BY seq DESC
            LIMIT 1;

            IF prev_row_hash IS NULL THEN
                IF NEW.prev_hash <> 'GENESIS' THEN
                    RAISE EXCEPTION 'audit_log chain break: first row prev_hash must be GENESIS, got %',
                        NEW.prev_hash;
                END IF;
            ELSE
                IF NEW.prev_hash <> prev_row_hash THEN
                    RAISE EXCEPTION 'audit_log chain break at seq=%: prev_hash % does not match previous row_hash %',
                        NEW.seq, NEW.prev_hash, prev_row_hash;
                END IF;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER audit_log_chain_check
        BEFORE INSERT ON audit_log
        FOR EACH ROW EXECUTE FUNCTION audit_log_verify_chain();
        """
    )

    # Append-only enforcement: REVOKE UPDATE/DELETE from PUBLIC. Grants for
    # the application role are added by the platform bootstrap runbook.
    op.execute("REVOKE UPDATE, DELETE ON audit_log FROM PUBLIC;")

    # ── idempotency_records ──────────────────────────────────────────────
    # One statement per op.execute — asyncpg cannot prepare multi-stmt SQL.
    op.execute(
        """
        CREATE TABLE idempotency_records (
            key           TEXT PRIMARY KEY,
            user_id       UUID,
            endpoint      TEXT NOT NULL,
            request_hash  TEXT NOT NULL,
            response_code INTEGER,
            response_body JSONB,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
            completed_at  TIMESTAMPTZ
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_idempotency_records_created_at "
        "ON idempotency_records (created_at);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS idempotency_records;")
    op.execute("DROP TRIGGER IF EXISTS audit_log_chain_check ON audit_log;")
    op.execute("DROP FUNCTION IF EXISTS audit_log_verify_chain();")
    op.execute("DROP TABLE IF EXISTS audit_log;")
    op.execute("DROP TABLE IF EXISTS users;")
