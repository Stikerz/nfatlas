"""Outbox writer — the sole INSERT path for the `outbox` table.

Callers pass their AsyncSession; the emit is on that session so the
outbox row commits (or rolls back) with the caller's state change —
this is the ADR-002 §Idempotency guarantee.

Payload validation happens against `EVENT_SCHEMAS[event_name]` before
insert. A producer that omits a required field fails at emit time,
never in the worker.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.events import EVENT_SCHEMAS
from atlas.outbox.models import OutboxRow


async def emit(
    session: AsyncSession,
    *,
    event_name: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
    correlation_id: str | None = None,
) -> OutboxRow:
    """Insert an outbox row on the caller's session.

    Raises `ValueError` if `event_name` is not in `EVENT_SCHEMAS` or if
    `payload` fails schema validation. Does not commit — the caller
    owns the transaction boundary.
    """
    schema = EVENT_SCHEMAS.get(event_name)
    if schema is None:
        raise ValueError(
            f"unknown event_name: {event_name!r} — declare it in atlas.events"
        )
    try:
        schema.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"invalid payload for {event_name}: {exc}") from exc

    row = OutboxRow(
        event_name=event_name,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=payload,
        correlation_id=correlation_id,
    )
    session.add(row)
    await session.flush()
    return row
