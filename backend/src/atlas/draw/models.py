"""Draw ORM models (ADR-006 §Protocol stages).

V0.5 uses this row as a read-only reference for tickets. Week 6 adds
the state-transition helpers (`commit`, `close`, `reveal`) and the
`server_seed_encrypted` decryption path. Until then:

  state    is fixed at 'sales_open' for the seeded demo draw.
  commitment  is populated by the seed script (SHA-256(seed || draw_id)).
  server_seed_encrypted  is a plaintext base64 seed for V0.5 (see
    week-5-build-plan §0 ask 5 — encrypted-at-rest lands Week 6).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from atlas.db import Base


class Draw(Base):
    __tablename__ = "draws"
    __table_args__ = (
        CheckConstraint("ticket_price_minor > 0", name="ticket_price_positive"),
        CheckConstraint(
            "state IN ('draft', 'committed', 'sales_open', 'sales_closed', 'revealed')",
            name="state_enum",
        ),
        CheckConstraint("close_time <= draw_time", name="close_before_draw"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    prize_copy: Mapped[str] = mapped_column(String, nullable=False)
    ticket_price_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("'NGN'")
    )
    entries_cap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    close_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    draw_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    state: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("'draft'")
    )
    commitment: Mapped[str] = mapped_column(String, nullable=False)
    server_seed_encrypted: Mapped[str] = mapped_column(String, nullable=False)
    tickets_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    revealed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reveal_inputs: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class DrawWinner(Base):
    __tablename__ = "draw_winners"
    __table_args__ = (
        CheckConstraint("position >= 0", name="position_non_negative"),
        CheckConstraint(
            "(position = 0) = is_primary", name="primary_at_position_zero"
        ),
        CheckConstraint(
            "contact_status IN ('pending', 'contacted', 'claimed', 'declined', 'expired')",
            name="contact_status_enum",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    draw_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("draws.id"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False)
    contact_status: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("'pending'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
