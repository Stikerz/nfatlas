"""Re-encrypt legacy raw-hex server_seed rows with Fernet (Day 1 W8)

Revision ID: 0010_encrypt_server_seed
Revises: 0009_draw_winners
Create Date: 2026-08-24 09:00

- No schema change. `draws.server_seed_encrypted` (TEXT) already fits a
  Fernet token (44-char url-safe b64 for a 32-byte plaintext + IV, plus
  version + timestamp — total ~100 chars).
- Data migration: any row whose value is a 64-char raw-hex string (the
  V0.5 plaintext debt per week-5-build-plan §0 ask 5) is decoded and
  re-encrypted with the ADR-006 §Stage 1 Fernet key.
- Idempotent: rows that already look like a Fernet token (`gAAAAA...`
  prefix) are skipped. Rows that match neither shape fail loudly so an
  operator investigates before we destroy data.
- Downgrade path: not automatic. Reversing to plaintext hex requires
  the operator to know the key and consciously downgrade a security
  control — kept as a manual runbook step, not a one-command action.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = "0010_encrypt_server_seed"
down_revision: Union[str, None] = "0009_draw_winners"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Late import so the Alembic env doesn't demand the crypto stack for
    # every migration in a fresh boot (0001..0009 pre-date this dep).
    from atlas.draw import crypto

    conn = op.get_bind()
    rows = conn.execute(
        text("SELECT id, server_seed_encrypted FROM draws")
    ).fetchall()

    for row_id, encoded in rows:
        if not encoded:
            raise RuntimeError(
                f"draws.id={row_id} has empty server_seed_encrypted — "
                "unreachable via app code; investigate before re-running."
            )
        if encoded.startswith("gAAAAA"):
            continue  # already encrypted
        if len(encoded) == 64:
            try:
                seed = bytes.fromhex(encoded)
            except ValueError as exc:
                raise RuntimeError(
                    f"draws.id={row_id} looks 64-char but is not hex: {exc}"
                ) from exc
            if len(seed) != 32:
                raise RuntimeError(
                    f"draws.id={row_id} hex decodes to {len(seed)} bytes, "
                    "expected 32."
                )
            token = crypto.encrypt_server_seed(seed)
            conn.execute(
                text(
                    "UPDATE draws SET server_seed_encrypted = :token "
                    "WHERE id = :id"
                ),
                {"token": token, "id": row_id},
            )
            continue

        raise RuntimeError(
            f"draws.id={row_id} server_seed_encrypted matches neither "
            "raw-hex (64 chars) nor Fernet-token (gAAAAA... prefix). "
            f"Value prefix: {encoded[:12]!r}. Investigate before re-running."
        )


def downgrade() -> None:
    # Intentional no-op — reverse migration would decrypt every row back
    # to plaintext hex, weakening the security posture with a single
    # command. Operators who genuinely need to downgrade must do so via
    # the documented rotation runbook (docs/runbooks/secret-loss.md),
    # not via `alembic downgrade`.
    pass
