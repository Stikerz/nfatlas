"""skill_question_attempts (Day 2 W5)

Revision ID: 0007_skill_question_attempts
Revises: 0006_draws_skill_questions
Create Date: 2026-07-29 09:00

One row per user × question attempt. Carries:
  - `is_correct`      — set by verify_answer.
  - `entitlement_expires_at` — set when is_correct=true; the ticket-
    purchase route (Day 3) consumes the attempt as an entitlement
    against this expiry.
  - `consumed_at`     — set by Day 3's ticket-purchase path; nullable
    until then. attempt_id doubles as the entitlement identifier
    (simpler than a separate UUID — same lifetime, same audit trail).

Column-level guards live in the service (verify_answer / ticket
purchase) — the DB constraints here are minimal so the audit trail
carries the semantic history even for edge cases.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0007_skill_question_attempts"
down_revision: Union[str, None] = "0006_draws_skill_questions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE skill_question_attempts (
            id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id                  UUID NOT NULL REFERENCES users(id),
            draw_id                  UUID NOT NULL REFERENCES draws(id),
            question_id              UUID NOT NULL REFERENCES skill_questions(id),
            issued_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
            expires_at               TIMESTAMPTZ NOT NULL,
            answered_at              TIMESTAMPTZ,
            is_correct               BOOLEAN,
            entitlement_expires_at   TIMESTAMPTZ,
            consumed_at              TIMESTAMPTZ
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_skill_question_attempts_user_draw "
        "ON skill_question_attempts (user_id, draw_id, issued_at DESC);"
    )
    op.execute(
        "CREATE INDEX ix_skill_question_attempts_entitlement_live "
        "ON skill_question_attempts (id) "
        "WHERE is_correct = TRUE AND consumed_at IS NULL;"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS skill_question_attempts;")
