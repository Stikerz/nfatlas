"""Read-only audit-log query helpers for the admin surface.

Separate module from `writer.py` to keep the "sole insert path"
grep-enforcement clean — admin reads are OK from anywhere per ADR-005;
writes are the invariant.
"""

from __future__ import annotations

import itertools
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog
from atlas.audit_log.writer import GENESIS_HASH, compute_row_hash


async def query(
    session: AsyncSession,
    *,
    event_name: str | None = None,
    subject_type: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 50,
    before_seq: int | None = None,
) -> list[AuditLog]:
    """Newest-first ranked audit rows matching the filters.

    Pagination: `before_seq` as an anchor — pass the smallest `seq`
    returned in the previous page. `limit` is capped at 500 at the
    caller (route validates); this function trusts its input.
    """
    stmt = select(AuditLog).order_by(AuditLog.seq.desc()).limit(limit)
    if event_name:
        stmt = stmt.where(AuditLog.event_name == event_name)
    if subject_type:
        stmt = stmt.where(AuditLog.subject_type == subject_type)
    if since:
        stmt = stmt.where(AuditLog.occurred_at >= since)
    if until:
        stmt = stmt.where(AuditLog.occurred_at <= until)
    if before_seq is not None:
        stmt = stmt.where(AuditLog.seq < before_seq)

    rows = (await session.execute(stmt)).scalars().all()
    return list(rows)


def verify_chain_page(rows: list[AuditLog]) -> tuple[bool, str | None]:
    """Verify that the rows form a valid contiguous chain slice.

    Returns (ok, reason). `ok=False` means at least one row's
    `row_hash` doesn't match the recomputed canonical hash, OR the
    prev_hash of row N doesn't equal the row_hash of row N-1 (with
    the special-case that the last row in the slice — smallest seq —
    is not verified against a prior row, since prior may be outside
    the page).
    """
    if not rows:
        return True, None

    # Rows are newest-first (seq DESC). Verify each row's row_hash
    # matches the canonical recomputation. Chain linkage is verified
    # only between adjacent rows within the returned slice.
    ordered = sorted(rows, key=lambda r: r.seq)  # ascending

    for row in ordered:
        expected = compute_row_hash(
            seq=row.seq,
            occurred_at=row.occurred_at,
            actor_type=row.actor_type,
            actor_id=row.actor_id,
            event_name=row.event_name,
            subject_type=row.subject_type,
            subject_id=row.subject_id,
            payload=row.payload,
            prev_hash=row.prev_hash,
        )
        if expected != row.row_hash:
            return False, f"row_hash mismatch at seq={row.seq}"

    for prev, curr in itertools.pairwise(ordered):
        if curr.prev_hash != prev.row_hash:
            return False, f"chain break at seq={curr.seq}"

    return True, None


def to_dict(row: AuditLog) -> dict[str, Any]:
    return {
        "seq": row.seq,
        "occurred_at": row.occurred_at.isoformat(),
        "actor_type": row.actor_type,
        "actor_id": row.actor_id,
        "event_name": row.event_name,
        "subject_type": row.subject_type,
        "subject_id": row.subject_id,
        "payload": row.payload,
        "prev_hash": row.prev_hash,
        "row_hash": row.row_hash,
    }


__all__ = ["GENESIS_HASH", "query", "to_dict", "verify_chain_page"]
