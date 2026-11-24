"""self_exclusions (ADR-010 Phase A)

Revision ID: 0012_self_exclusions
Revises: 0011_outbox
Create Date: 2026-11-24 09:00

Per the ADR-010 amendment of 2026-11-24.

- `self_exclusions`: keyed on `user_id`, NOT on `bvn_hash` as the base
  ADR specified. BVN is collected nowhere in the system (ADR-007/KYC
  is unbuilt), so a bvn-keyed PK has nothing to key on. `bvn_hash` is
  created here as a nullable UNIQUE column so Phase B is a backfill
  rather than a migration of a live table.
- Sole writer is `atlas.identity.self_exclusion`.
- No reversal: V1 exclusion is permanent, so there is deliberately no
  `revoked_at` column and no un-exclude path. Absence of the capability
  is the enforcement.
- `users.status = 'closed'` already exists in the status CHECK and was
  never set by anything; the exclusion service is its first writer.
  No schema change needed there.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0012_self_exclusions"
down_revision: Union[str, None] = "0011_outbox"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE self_exclusions (
            user_id        UUID PRIMARY KEY REFERENCES users(id),
            bvn_hash       TEXT UNIQUE,
            excluded_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
            excluded_by    TEXT NOT NULL,
            excluded_by_id UUID REFERENCES users(id),
            reason         TEXT,
            notes          TEXT,
            CONSTRAINT ck_self_exclusions_excluded_by_enum
                CHECK (excluded_by IN ('user_self', 'operator', 'regulator'))
        );
        """
    )
    # Phase B lookup path. Partial — every Phase A row has a NULL hash,
    # and NULLs carry no useful index entry.
    op.execute(
        "CREATE INDEX idx_self_exclusions_bvn_hash "
        "ON self_exclusions (bvn_hash) WHERE bvn_hash IS NOT NULL;"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS self_exclusions;")
