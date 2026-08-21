"""Outbox event-name → handler registry (ADR-002 §Processing model).

A handler is `async def handler(session: AsyncSession, payload: dict) -> None`.
The worker calls the handler inside its own transaction; the handler shares
the session so any DB reads see the same connection as the outbox row lock.

Registration is static (import-time). W8 lands one handler; W9 adds more.
"""

from __future__ import annotations

from typing import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.events import WINNER_SELECTED_V1
from atlas.notification.winner import deliver_from_payload as _deliver_winner

Handler = Callable[[AsyncSession, dict], Awaitable[None]]

HANDLERS: dict[str, Handler] = {
    WINNER_SELECTED_V1: _deliver_winner,
}
