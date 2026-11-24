"""Ticket request/response Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PurchaseTicketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draw_id: uuid.UUID
    entitlement_id: uuid.UUID  # the skill_question_attempt id


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
