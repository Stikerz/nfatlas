"""Draw request/response Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class CreateDrawRequest(BaseModel):
    """POST /api/v1/draws — admin creates a fresh sales_open draw."""

    model_config = ConfigDict(extra="forbid")

    prize_copy: str = Field(min_length=1, max_length=500)
    ticket_price_minor: int = Field(gt=0)
    close_time: datetime
    draw_time: datetime
    entries_cap: int | None = Field(default=None, gt=0)


class DrawCloseResponse(BaseModel):
    """Return shape from POST /draws/{id}/close."""

    id: uuid.UUID
    state: str
    tickets_hash: str
    close_time: datetime
    draw_time: datetime


class DrawRevealResponse(BaseModel):
    """Return shape from POST /draws/{id}/reveal."""

    id: uuid.UUID
    state: str
    revealed_at: datetime
    winner_count: int


class WinnerSummary(BaseModel):
    position: int
    is_primary: bool
    ticket_id: uuid.UUID
    user_id: uuid.UUID
    contact_status: str


class ClaimResponse(BaseModel):
    draw_id: uuid.UUID
    ticket_id: uuid.UUID
    position: int
    is_primary: bool
    contact_status: str


class WinnerList(BaseModel):
    items: list[WinnerSummary]


class WinnerProof(BaseModel):
    """Winner shape in the public proof — user_id_hash only, never raw."""

    position: int
    is_primary: bool
    ticket_id: uuid.UUID
    user_id_hash: str


class EntropyProof(BaseModel):
    mode: str
    bitcoin_hash: str
    bitcoin_height: int
    bitcoin_timestamp: int
    drand_round: int
    drand_randomness: str
    drand_signature: str
    verified_at: str


class DrawProof(BaseModel):
    """Public proof endpoint response.

    Pre-reveal (state != 'revealed'): only the pre-reveal fields are
    populated; post-reveal fields are None. Post-reveal: everything
    a third-party verifier needs to re-run select_winners and reach
    the same winner.

    Explicit schema — no user emails, no phone_e164, no ticket owner
    identifiers beyond the SHA-256 hash. Adaeze §5 posture.
    """

    id: uuid.UUID
    state: str
    commitment: str
    close_time: datetime
    draw_time: datetime

    # Post-reveal only.
    revealed_at: datetime | None = None
    server_seed: str | None = None
    tickets_hash: str | None = None
    ticket_count: int | None = None
    ordered_ticket_ids: list[uuid.UUID] | None = None
    entropy: EntropyProof | None = None
    winners: list[WinnerProof] | None = None
    algorithm_reference: str | None = None
    reserves: int | None = None
