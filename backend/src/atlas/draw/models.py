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

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
