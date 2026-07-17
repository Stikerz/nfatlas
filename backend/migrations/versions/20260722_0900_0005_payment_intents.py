"""payment_intents table (Day 3 W4)

Revision ID: 0005_payment_intents
Revises: 0004_ledger
Create Date: 2026-07-22 09:00

Implements ADR-008 §Protocol surface (PaymentStatus enum) + week-4-build-plan
§Day 3. Per ADR-004, the client-supplied Idempotency-Key is stored UNIQUE
on this table; a retry with the same key returns the cached row instead of
minting a second intent at the vendor.

Columns:
  id                UUID pk
  user_id           UUID (fk users.id)
  amount_minor      BIGINT, kobo
  currency          TEXT, 'NGN' default
  method            TEXT, PaymentMethod enum
  status            TEXT, PaymentStatus enum, 'initiated' default
  vendor            TEXT, 'paystack' V1
  vendor_reference  TEXT, nullable (set on adapter response)
  checkout_url      TEXT, nullable (set on adapter response)
  idempotency_key   TEXT, UNIQUE (ADR-004)
  description       TEXT
  metadata          JSONB, default '{}'::jsonb
  raw_response      JSONB, redacted vendor response snapshot (ADR-008)
  created_at        TIMESTAMPTZ default now()
  updated_at        TIMESTAMPTZ default now()

State machine per ADR-008 §Protocol surface: initiated → pending →
succeeded / failed / refunded / partially_refunded. Enforced in service
code; the CHECK constraint just guards against typos.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0005_payment_intents"
down_revision: Union[str, None] = "0004_ledger"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # One statement per op.execute — asyncpg cannot prepare multi-stmt SQL.
    op.execute(
        """
        CREATE TABLE payment_intents (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id          UUID NOT NULL REFERENCES users(id),
            amount_minor     BIGINT NOT NULL,
            currency         TEXT NOT NULL DEFAULT 'NGN',
            method           TEXT NOT NULL,
            status           TEXT NOT NULL DEFAULT 'initiated',
            vendor           TEXT NOT NULL DEFAULT 'paystack',
            vendor_reference TEXT,
            checkout_url     TEXT,
            idempotency_key  TEXT NOT NULL,
            description      TEXT NOT NULL DEFAULT '',
            metadata         JSONB NOT NULL DEFAULT '{}'::jsonb,
            raw_response     JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_payment_intents_amount_positive
                CHECK (amount_minor > 0),
            CONSTRAINT ck_payment_intents_method_enum
                CHECK (method IN ('card', 'bank_transfer', 'ussd', 'mobile_money')),
            CONSTRAINT ck_payment_intents_status_enum
                CHECK (status IN (
                    'initiated', 'pending', 'succeeded',
                    'failed', 'refunded', 'partially_refunded'
                )),
            CONSTRAINT ck_payment_intents_vendor_enum
                CHECK (vendor IN ('paystack'))
        );
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_payment_intents_idempotency_key "
        "ON payment_intents (idempotency_key);"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_payment_intents_vendor_reference "
        "ON payment_intents (vendor_reference) "
        "WHERE vendor_reference IS NOT NULL;"
    )
    op.execute(
        "CREATE INDEX ix_payment_intents_user_id_created_at "
        "ON payment_intents (user_id, created_at DESC);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS payment_intents;")
