"""tickets + free_entry_slips + payment_intents.purpose (Day 3 W5)

Revision ID: 0008_tickets_and_free_slips
Revises: 0007_skill_question_attempts
Create Date: 2026-07-30 09:00

- `tickets`: one row per issued ticket. `ticket_number` is monotonic
  per draw (allocated under a draw-row SELECT FOR UPDATE inside
  ticket.service._mint_ticket — see that module for the concurrency
  contract). `entry_source` enum discriminates paid vs free. The
  ledger transaction id or the free-slip reference lives in
  `external_ref` for cross-linking.
- `free_entry_slips`: one row per admin-transcribed free entry.
  UNIQUE (draw_id, slip_reference) — the same slip cannot be
  transcribed twice into the same draw (Adaeze §5 audit-trail).
- `payment_intents.purpose`: 'deposit' | 'ticket'. Default 'deposit'
  preserves W4 shape. Ticket-purpose intents carry the entitlement id
  + draw id in `metadata` for webhook dispatch.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0008_tickets_and_free_slips"
down_revision: Union[str, None] = "0007_skill_question_attempts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── tickets ──────────────────────────────────────────────────────────
    op.execute(
        """
        CREATE TABLE tickets (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            draw_id          UUID NOT NULL REFERENCES draws(id),
            user_id          UUID NOT NULL REFERENCES users(id),
            ticket_number    INTEGER NOT NULL,
            entry_source     TEXT NOT NULL,
            external_ref     TEXT,
            idempotency_key  TEXT NOT NULL,
            issued_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_tickets_entry_source_enum
                CHECK (entry_source IN ('paid', 'free')),
            CONSTRAINT ck_tickets_ticket_number_positive
                CHECK (ticket_number > 0)
        );
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_tickets_draw_ticket_number "
        "ON tickets (draw_id, ticket_number);"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_tickets_idempotency_key "
        "ON tickets (idempotency_key);"
    )
    op.execute(
        "CREATE INDEX ix_tickets_user_issued "
        "ON tickets (user_id, issued_at DESC);"
    )

    # ── free_entry_slips ────────────────────────────────────────────────
    op.execute(
        """
        CREATE TABLE free_entry_slips (
            id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            draw_id            UUID NOT NULL REFERENCES draws(id),
            slip_reference     TEXT NOT NULL,
            actor_operator_id  UUID NOT NULL REFERENCES users(id),
            subject_user_id    UUID NOT NULL REFERENCES users(id),
            created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_free_entry_slips_draw_reference "
        "ON free_entry_slips (draw_id, slip_reference);"
    )

    # ── payment_intents.purpose ────────────────────────────────────────
    op.execute(
        "ALTER TABLE payment_intents "
        "ADD COLUMN purpose TEXT NOT NULL DEFAULT 'deposit';"
    )
    op.execute(
        "ALTER TABLE payment_intents "
        "ADD CONSTRAINT ck_payment_intents_purpose_enum "
        "CHECK (purpose IN ('deposit', 'ticket'));"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE payment_intents DROP CONSTRAINT IF EXISTS "
        "ck_payment_intents_purpose_enum;"
    )
    op.execute("ALTER TABLE payment_intents DROP COLUMN IF EXISTS purpose;")
    op.execute("DROP TABLE IF EXISTS free_entry_slips;")
    op.execute("DROP TABLE IF EXISTS tickets;")
