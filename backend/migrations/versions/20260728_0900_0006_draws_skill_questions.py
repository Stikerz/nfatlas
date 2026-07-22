"""draws + skill_questions + skill_question_options (Day 1 W5)

Revision ID: 0006_draws_skill_questions
Revises: 0005_payment_intents
Create Date: 2026-07-28 09:00

Implements the Week 5 slice of ADR-006:
  - `draws` — the row that the Week 6 reveal path consumes. V0.5 only
    exercises `state='sales_open'`; the other states are reserved for
    Week 6 (`draft`/`committed` before, `sales_closed`/`revealed`
    after). `commitment` + `server_seed_encrypted` are present per
    ADR-006 §Protocol stage 1 — TODO(week-6): encryption at rest lands
    with the draw-engine module. V0.5 stores the seed plaintext per the
    founder decision recorded in week-5-build-plan.md §0 ask 5.
  - `skill_questions` + `skill_question_options` — pool of multiple-
    choice questions per week-5-build-plan §0 ask 3. Options carry the
    is_correct flag (never returned by the API on next-question — only
    consulted by verify_answer).

Not in this migration (arrive later this week):
  - `skill_question_attempts` (Day 2, migration 0007).
  - `tickets` + `free_entry_slips` (Day 3, migration 0008).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0006_draws_skill_questions"
down_revision: Union[str, None] = "0005_payment_intents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── draws ────────────────────────────────────────────────────────────
    # One statement per op.execute — asyncpg cannot prepare multi-stmt SQL.
    op.execute(
        """
        CREATE TABLE draws (
            id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            prize_copy             TEXT NOT NULL,
            ticket_price_minor     BIGINT NOT NULL,
            currency               TEXT NOT NULL DEFAULT 'NGN',
            entries_cap            INTEGER,
            close_time             TIMESTAMPTZ NOT NULL,
            draw_time              TIMESTAMPTZ NOT NULL,
            state                  TEXT NOT NULL DEFAULT 'draft',
            commitment             TEXT NOT NULL,
            server_seed_encrypted  TEXT NOT NULL,
            tickets_hash           TEXT,
            revealed_at            TIMESTAMPTZ,
            created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_draws_ticket_price_positive
                CHECK (ticket_price_minor > 0),
            CONSTRAINT ck_draws_state_enum
                CHECK (state IN (
                    'draft', 'committed', 'sales_open',
                    'sales_closed', 'revealed'
                )),
            CONSTRAINT ck_draws_close_before_draw
                CHECK (close_time <= draw_time)
        );
        """
    )
    op.execute("CREATE INDEX ix_draws_state ON draws (state);")
    op.execute("CREATE INDEX ix_draws_close_time ON draws (close_time);")

    # ── skill_questions ──────────────────────────────────────────────────
    op.execute(
        """
        CREATE TABLE skill_questions (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            prompt      TEXT NOT NULL,
            active      BOOLEAN NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_skill_questions_active ON skill_questions (active);"
    )

    # ── skill_question_options ──────────────────────────────────────────
    op.execute(
        """
        CREATE TABLE skill_question_options (
            id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            question_id  UUID NOT NULL REFERENCES skill_questions(id) ON DELETE CASCADE,
            option_text  TEXT NOT NULL,
            is_correct   BOOLEAN NOT NULL DEFAULT FALSE,
            display_order INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_skill_question_options_question "
        "ON skill_question_options (question_id, display_order);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS skill_question_options;")
    op.execute("DROP TABLE IF EXISTS skill_questions;")
    op.execute("DROP TABLE IF EXISTS draws;")
