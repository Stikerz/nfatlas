"""Ticket request/response Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PurchaseTicketRequest(BaseModel):
    """Entry purchase. The skill-question entitlement was removed on
    2026-11-26 (AMEND-003) — lawfulness rests on the State gaming licence,
    not on a draw mechanic, so there is nothing to gate the purchase on
    beyond the draw being open and the buyer not being self-excluded."""

    model_config = ConfigDict(extra="forbid")

    draw_id: uuid.UUID


class PurchaseTicketResponse(BaseModel):
    """Kicks off checkout — the ticket itself is minted on the webhook."""

    payment_intent_id: uuid.UUID
    vendor_reference: str
    checkout_url: str | None
    amount_minor: int
    currency: str
    expires_at: datetime | None


class TicketSummary(BaseModel):
    id: uuid.UUID
    draw_id: uuid.UUID
    ticket_number: int
    entry_source: str
    issued_at: datetime


class TicketList(BaseModel):
    items: list[TicketSummary]
