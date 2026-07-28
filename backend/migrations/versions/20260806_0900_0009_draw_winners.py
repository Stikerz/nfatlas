"""draw_winners + draws.reveal_inputs (Day 3 W6)

Revision ID: 0009_draw_winners
Revises: 0008_tickets_and_free_slips
Create Date: 2026-08-06 09:00

- `draw_winners`: one row per selected ticket. `position=0` is the
  primary winner; 1..N are reserves in selection order. UNIQUE
  (draw_id, position) enforces the ordering; UNIQUE (draw_id,
  ticket_id) enforces the "distinct" property of the algorithm.
  `contact_status` tracks the prize-fulfilment state — V0.5 only
  populates 'pending' at reveal; Week 7 claim UX advances it.
- `draws.reveal_inputs`: JSONB blob of the proof-time entropy
  (bitcoin_hash, bitcoin_height, drand_round, drand_randomness,
  drand_signature, verified_at, mode). Persisted so the /proof
  endpoint (Day 4) can serve them without re-fetching entropy.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0009_draw_winners"
down_revision: Union[str, None] = "0008_tickets_and_free_slips"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE draw_winners (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            draw_id         UUID NOT NULL REFERENCES draws(id),
            position        INTEGER NOT NULL,
            ticket_id       UUID NOT NULL REFERENCES tickets(id),
            user_id         UUID NOT NULL REFERENCES users(id),
            is_primary      BOOLEAN NOT NULL,
            contact_status  TEXT NOT NULL DEFAULT 'pending',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_draw_winners_position_non_negative
                CHECK (position >= 0),
            CONSTRAINT ck_draw_winners_primary_at_position_zero
                CHECK ((position = 0) = is_primary),
            CONSTRAINT ck_draw_winners_contact_status_enum
                CHECK (contact_status IN (
                    'pending', 'contacted', 'claimed', 'declined', 'expired'
                ))
        );
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_draw_winners_draw_position "
        "ON draw_winners (draw_id, position);"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_draw_winners_draw_ticket "
        "ON draw_winners (draw_id, ticket_id);"
    )
    op.execute(
        "CREATE INDEX ix_draw_winners_user "
        "ON draw_winners (user_id);"
    )

    op.execute(
        "ALTER TABLE draws "
        "ADD COLUMN reveal_inputs JSONB NOT NULL DEFAULT '{}'::jsonb;"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE draws DROP COLUMN IF EXISTS reveal_inputs;")
    op.execute("DROP TABLE IF EXISTS draw_winners;")
