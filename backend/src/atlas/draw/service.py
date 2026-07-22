"""Draw service — read-only in V0.5.

Week 6 adds `commit_draw`, `close_draw`, `reveal_draw` per ADR-006
§Protocol stages 3-4. V0.5 only exercises `sales_open` reads plus a
`is_sales_open` guard used by the ticket-purchase route to fail-fast
on closed / draft / revealed draws.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.draw.models import Draw


class DrawNotFoundError(LookupError):
    """Draw id does not exist."""


class DrawNotOpenError(RuntimeError):
    """Draw exists but is not accepting new entries."""


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
