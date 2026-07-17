"""ledger_accounts + ledger_entries + deferred balance trigger (Day 1 W4)

Revision ID: 0004_ledger
Revises: 0003_rbac
Create Date: 2026-07-21 09:00

Implements ADR-003 §Schema + §Invariants:
  - ledger_accounts + partial unique (NULLS NOT DISTINCT — PG 15+) so
    operator singletons stay singleton even with NULL owner_id.
  - ledger_entries with the D/C direction + amount_positive constraints
    and the partial-unique idempotency index.
  - Chart-of-accounts seed for the 4 operator-level singleton rows.
    user_wallet + prize_pool remain lazily-created by the service layer.
  - Constraint trigger `ledger_transaction_balance` DEFERRABLE INITIALLY
    DEFERRED — fires per row but checks at COMMIT so a multi-entry
    transaction inserts all sides before the sum is validated.
  - Append-only enforcement: REVOKE UPDATE, DELETE ON ledger_entries
    FROM PUBLIC.

Note on the trigger: it re-runs the SUM query for each inserted row (N²
work per transaction). Fine at V0.5 volumes; a session-variable / memo
optimisation is a Week 6+ concern.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0004_ledger"
down_revision: Union[str, None] = "0003_rbac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── ledger_accounts ──────────────────────────────────────────────────
    op.execute(
        """
        CREATE TABLE ledger_accounts (
            id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            account_type TEXT NOT NULL,
            owner_type   TEXT NOT NULL,
            owner_id     TEXT,
            currency     TEXT NOT NULL DEFAULT 'NGN',
            created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_ledger_accounts_account_type_enum
                CHECK (account_type IN (
                    'user_wallet', 'operator_revenue', 'prize_pool',
                    'refund_payable', 'payment_gateway_clearing', 'tax_payable'
                )),
            CONSTRAINT ck_ledger_accounts_owner_type_enum
                CHECK (owner_type IN ('user', 'operator', 'draw', 'gateway')),
            CONSTRAINT uq_ledger_accounts_identity
                UNIQUE NULLS NOT DISTINCT (account_type, owner_type, owner_id, currency)
        );
        """
    )

    # ── ledger_entries ───────────────────────────────────────────────────
    # One statement per op.execute — asyncpg cannot prepare multi-stmt SQL.
    op.execute(
        """
        CREATE TABLE ledger_entries (
            id               BIGSERIAL PRIMARY KEY,
            transaction_id   UUID NOT NULL,
            account_id       UUID NOT NULL REFERENCES ledger_accounts(id),
            direction        CHAR(1) NOT NULL,
            amount_minor     BIGINT NOT NULL,
            currency         TEXT NOT NULL DEFAULT 'NGN',
            posted_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
            description      TEXT NOT NULL,
            external_ref     TEXT,
            idempotency_key  TEXT,
            metadata         JSONB NOT NULL DEFAULT '{}'::jsonb,
            CONSTRAINT ck_ledger_entries_direction_enum
                CHECK (direction IN ('D', 'C')),
            CONSTRAINT ck_ledger_entries_amount_positive
                CHECK (amount_minor > 0)
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_ledger_entries_account_posted "
        "ON ledger_entries (account_id, posted_at);"
    )
    op.execute(
        "CREATE INDEX ix_ledger_entries_transaction "
        "ON ledger_entries (transaction_id);"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_ledger_entries_idempotency "
        "ON ledger_entries (idempotency_key) "
        "WHERE idempotency_key IS NOT NULL;"
    )

    # ── Deferred balance-check constraint trigger ────────────────────────
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ledger_transaction_balance_check()
        RETURNS TRIGGER AS $$
        DECLARE
            net_amount BIGINT;
        BEGIN
            SELECT COALESCE(
                SUM(CASE direction WHEN 'C' THEN amount_minor ELSE -amount_minor END),
                0
            ) INTO net_amount
            FROM ledger_entries
            WHERE transaction_id = NEW.transaction_id;

            IF net_amount != 0 THEN
                RAISE EXCEPTION
                    'ledger transaction % is unbalanced: net = % kobo',
                    NEW.transaction_id, net_amount;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER ledger_transaction_balance
        AFTER INSERT ON ledger_entries
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION ledger_transaction_balance_check();
        """
    )

    # ── Append-only enforcement (ADR-003 §Invariants 3) ──────────────────
    op.execute("REVOKE UPDATE, DELETE ON ledger_entries FROM PUBLIC;")

    # ── Chart-of-accounts seed: 4 operator-level singletons ──────────────
    op.execute(
        """
        INSERT INTO ledger_accounts (account_type, owner_type, owner_id, currency) VALUES
          ('operator_revenue',         'operator', NULL,       'NGN'),
          ('refund_payable',           'operator', NULL,       'NGN'),
          ('payment_gateway_clearing', 'gateway',  'paystack', 'NGN'),
          ('tax_payable',              'operator', NULL,       'NGN');
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS ledger_transaction_balance ON ledger_entries;")
    op.execute("DROP FUNCTION IF EXISTS ledger_transaction_balance_check();")
    op.execute("DROP TABLE IF EXISTS ledger_entries;")
    op.execute("DROP TABLE IF EXISTS ledger_accounts;")
