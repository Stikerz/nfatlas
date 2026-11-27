"""draws.prize_image_url (SPIKE — prize photography)

Revision ID: 0013_prize_image
Revises: 0012_self_exclusions
Create Date: 2026-11-27 09:00

Wireframe 16 §4.1: the tone doc says "prize photography dominates the
fold", and the draw card has only ever carried text. In a carousel of
near-identical text cards that reads as a spreadsheet.

Nullable on purpose — every existing draw has no image, and a draw
without one must still render. The card falls back to the text-only
treatment rather than breaking.

NOTE: this is a spike to evaluate the treatment. A production version
needs an operator upload flow and somewhere to host the files; a bare
URL column trusts whatever the operator pastes. See §Follow-ups in
wireframe 16.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0013_prize_image"
down_revision: Union[str, None] = "0012_self_exclusions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE draws ADD COLUMN prize_image_url TEXT;")


def downgrade() -> None:
    op.execute("ALTER TABLE draws DROP COLUMN IF EXISTS prize_image_url;")
