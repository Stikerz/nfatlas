"""outbox + outbox_dead_letter (Day 2 W8)

Revision ID: 0011_outbox
Revises: 0010_encrypt_server_seed
Create Date: 2026-08-25 09:00

- `outbox`: transactional outbox per ADR-002 §Outbox table. BIGSERIAL
  PK, event_name + aggregate_(type,id) for routing, JSONB payload,
  correlation_id for request-id propagation, retry bookkeeping
  (attempts, last_error, next_attempt_at). Partial index
  `outbox_unprocessed_idx` on next_attempt_at WHERE processed_at IS
  NULL — keeps the polling query cheap as processed rows accumulate.
- `outbox_dead_letter`: terminal storage for rows that hit the retry
  ceiling. Worker moves rows here on the 10th failed dispatch (Day 3).
- Writer is `atlas.outbox.writer.emit`; models in `atlas.outbox.models`.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0011_outbox"
down_revision: Union[str, None] = "0010_encrypt_server_seed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE outbox (
            id              BIGSERIAL PRIMARY KEY,
            event_name      TEXT NOT NULL,
            aggregate_type  TEXT NOT NULL,
            aggregate_id    TEXT NOT NULL,
            payload         JSONB NOT NULL,
            correlation_id  TEXT,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            processed_at    TIMESTAMPTZ,
            attempts        INTEGER NOT NULL DEFAULT 0,
            last_error      TEXT,
            next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        "CREATE INDEX outbox_unprocessed_idx "
        "ON outbox (next_attempt_at) "
        "WHERE processed_at IS NULL;"
    )
    op.execute(
        """
        CREATE TABLE outbox_dead_letter (
            id              BIGSERIAL PRIMARY KEY,
            original_id     BIGINT NOT NULL,
            event_name      TEXT NOT NULL,
            aggregate_type  TEXT NOT NULL,
            aggregate_id    TEXT NOT NULL,
            payload         JSONB NOT NULL,
            correlation_id  TEXT,
            created_at      TIMESTAMPTZ NOT NULL,
            attempts        INTEGER NOT NULL,
            last_error      TEXT,
            moved_at        TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS outbox_dead_letter;")
    op.execute("DROP TABLE IF EXISTS outbox;")
