"""Draw request/response Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class DrawSummary(BaseModel):
    """Shape returned by GET /draws and GET /draws/{id}."""

    id: uuid.UUID
    prize_copy: str
    ticket_price_minor: int
    currency: str
    close_time: datetime
    draw_time: datetime
    state: str
    commitment: str  # public per ADR-006 §Protocol stage 1


class DrawList(BaseModel):
    items: list[DrawSummary]
