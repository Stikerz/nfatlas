"""Draw service.

Read-only surface + state transitions per ADR-006 §Protocol stages 3-4.

Week 6 Day 1: `close_draw` — computes tickets_hash, flips state to
`sales_closed`, emits `draw.entries_snapshot` audit event.
Week 6 Day 3: `reveal_draw` — fetches entropy, decrypts server_seed,
runs `select_winners`, flips state to `revealed`, emits `draw.revealed`
+ `draw.winner_selected` audit events.

All state changes go through `state_machine.transition` — the sole
authority on legal moves. Callers pass current + action; get back the
next state string or an IllegalTransitionError.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime

import rfc8785
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.draw import state_machine
from atlas.draw.models import Draw
from atlas.ticket.models import Ticket


class DrawNotFoundError(LookupError):
    """Draw id does not exist."""


class DrawNotOpenError(RuntimeError):
    """Draw exists but is not accepting new entries."""


class DrawStateError(RuntimeError):
    """Wrapper around state_machine.IllegalTransitionError for callers
    that want a draw-service-typed error surface."""


async def get(session: AsyncSession, *, draw_id: uuid.UUID) -> Draw:
    row = (
        await session.execute(select(Draw).where(Draw.id == draw_id))
    ).scalar_one_or_none()
    if row is None:
        raise DrawNotFoundError(str(draw_id))
    return row


async def list_active(session: AsyncSession) -> list[Draw]:
    """All draws currently in `sales_open`. V0.5 seeds exactly one."""
    rows = (
        await session.execute(
            select(Draw).where(Draw.state == "sales_open").order_by(Draw.close_time)
        )
    ).scalars().all()
    return list(rows)


async def is_sales_open(session: AsyncSession, *, draw_id: uuid.UUID) -> bool:
    """True iff the draw exists and is in `sales_open`."""
    state = (
        await session.execute(select(Draw.state).where(Draw.id == draw_id))
    ).scalar_one_or_none()
    return state == "sales_open"


async def close_draw(session: AsyncSession, *, draw_id: uuid.UUID) -> Draw:
    """Snapshot the ticket list, compute the tickets_hash, flip state
    to `sales_closed`. Emits `draw.entries_snapshot` audit event with
    the ticket count + hash.

    Idempotent: calling close_draw on an already-closed draw returns
    the existing row (tickets_hash unchanged, no duplicate audit event).
    Calling on any other state raises DrawStateError.
    """
    draw = await get(session, draw_id=draw_id)

    if draw.state == state_machine.DrawState.SALES_CLOSED.value:
        return draw

    try:
        next_state = state_machine.transition(
            draw.state, state_machine.DrawAction.CLOSE.value
        )
    except state_machine.IllegalTransitionError as exc:
        raise DrawStateError(str(exc)) from exc

    ticket_ids = (
        await session.execute(
            select(Ticket.id)
            .where(Ticket.draw_id == draw_id)
            .order_by(Ticket.ticket_number)
        )
    ).scalars().all()
    tickets_hash = hashlib.sha256(
        rfc8785.dumps([str(t) for t in ticket_ids])
    ).hexdigest()

    draw.tickets_hash = tickets_hash
    draw.state = next_state
    draw.updated_at = datetime.now(UTC)
    await session.flush()

    await audit.append(
        session,
        actor_type="operator",
        actor_id="admin.close_draw",
        event_name="draw.entries_snapshot",
        subject_type="draw",
        subject_id=str(draw_id),
        payload={
            "draw_id": str(draw_id),
            "ticket_count": len(ticket_ids),
            "tickets_hash": tickets_hash,
        },
    )
    return draw
