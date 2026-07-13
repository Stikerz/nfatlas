"""Hash-chained audit log writer (ADR-005).

The ONLY module in the codebase permitted to INSERT into `audit_log`. Every
other module calls `append(...)` from here. Enforced by CI grep in
`.github/workflows/ci.yaml`.

Concurrency: writes are serialized inside the current transaction using a
namespace-scoped Postgres advisory lock. Two concurrent transactions attempting
to append will queue rather than race; both eventually succeed with correct
chain linkage.

Hash formula (ADR-005 §Hash chain):

    canonical = JCS-canonicalize({
        seq, occurred_at, actor_type, actor_id, event_name,
        subject_type, subject_id, payload, prev_hash
    })
    row_hash = SHA-256(canonical)

Where `seq` is the sequence value fetched from `nextval('audit_log_seq_seq')`
inside the same transaction, and `prev_hash` is either the row_hash of the
last row (SELECT ... ORDER BY seq DESC LIMIT 1) or the literal `'GENESIS'`.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Literal

import rfc8785
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog

GENESIS_HASH = "GENESIS"

# 64-bit signed integer identifier used with pg_advisory_xact_lock to serialize
# audit_log inserts within a transaction. Derived from SHA-256("audit_log_append")
# first 8 bytes as signed int for stability across restarts.
_APPEND_LOCK_KEY = 4_812_369_487_128_953_247

ActorType = Literal["user", "operator", "system", "agent"]


def _canonical_row_bytes(
    *,
    seq: int,
    occurred_at: datetime,
    actor_type: str,
    actor_id: str | None,
    event_name: str,
    subject_type: str,
    subject_id: str,
    payload: dict[str, Any],
    prev_hash: str,
) -> bytes:
    """Produce the RFC 8785 canonical bytes for a row.

    Datetime is serialised as an ISO-8601 UTC string with microsecond
    precision so canonicalization is deterministic across Python versions.
    """
    row = {
        "seq": seq,
        "occurred_at": occurred_at.astimezone(timezone.utc).isoformat(
            timespec="microseconds"
        ),
        "actor_type": actor_type,
        "actor_id": actor_id,
        "event_name": event_name,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    return rfc8785.dumps(row)


def compute_row_hash(
    *,
    seq: int,
    occurred_at: datetime,
    actor_type: str,
    actor_id: str | None,
    event_name: str,
    subject_type: str,
    subject_id: str,
    payload: dict[str, Any],
    prev_hash: str,
) -> str:
    """Deterministic SHA-256 hex of the canonical row. Public for verifier reuse."""
    return hashlib.sha256(
        _canonical_row_bytes(
            seq=seq,
            occurred_at=occurred_at,
            actor_type=actor_type,
            actor_id=actor_id,
            event_name=event_name,
            subject_type=subject_type,
            subject_id=subject_id,
            payload=payload,
            prev_hash=prev_hash,
        )
    ).hexdigest()


async def append(
    session: AsyncSession,
    *,
    actor_type: ActorType,
    actor_id: str | None,
    event_name: str,
    subject_type: str,
    subject_id: str,
    payload: dict[str, Any],
    occurred_at: datetime | None = None,
) -> AuditLog:
    """Append a new event to the audit log. Returns the persisted row.

    Runs entirely inside the caller's transaction. The caller is responsible
    for commit/rollback — this function does neither.
    """
    # Serialise concurrent appenders within the tx.
    await session.execute(
        text("SELECT pg_advisory_xact_lock(:key)"),
        {"key": _APPEND_LOCK_KEY},
    )

    prev_hash_row = await session.execute(
        text("SELECT row_hash FROM audit_log ORDER BY seq DESC LIMIT 1")
    )
    prev_hash = prev_hash_row.scalar_one_or_none() or GENESIS_HASH

    seq_result = await session.execute(text("SELECT nextval('audit_log_seq_seq')"))
    seq = int(seq_result.scalar_one())

    occurred = (occurred_at or datetime.now(timezone.utc)).astimezone(timezone.utc)

    row_hash = compute_row_hash(
        seq=seq,
        occurred_at=occurred,
        actor_type=actor_type,
        actor_id=actor_id,
        event_name=event_name,
        subject_type=subject_type,
        subject_id=subject_id,
        payload=payload,
        prev_hash=prev_hash,
    )

    entry = AuditLog(
        seq=seq,
        occurred_at=occurred,
        actor_type=actor_type,
        actor_id=actor_id,
        event_name=event_name,
        subject_type=subject_type,
        subject_id=subject_id,
        payload=payload,
        prev_hash=prev_hash,
        row_hash=row_hash,
    )
    session.add(entry)
    await session.flush()
    return entry
