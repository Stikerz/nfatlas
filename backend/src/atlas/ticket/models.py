"""Ticket ORM models.

`tickets`: sole INSERT path is atlas.ticket.service._mint_ticket (grep-
enforced Day 5). `ticket_number` monotonic per draw — see service
module for the allocation concurrency contract.

Free-entry route: unwired 2026-11-23 by founder decision. The
`FreeEntrySlip` ORM class and its writer (`service.issue_free`) are
removed, but the `free_entry_slips` table, its UNIQUE (draw_id,
slip_reference) index, and the `'free'` member of the `entry_source`
CHECK constraint are deliberately RETAINED and must not be dropped:

- `tickets` rows with `entry_source='free'` exist from earlier draws.
  Narrowing the constraint would invalidate them.
- Published commit-reveal proofs for those draws report the paid/free
  split (PRD §3.1); rewriting history would break a published proof.
- The ADR-005 audit chain carries `ticket.free_transcribed` entries.

Restoring the route means restoring code only — no migration.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from atlas.db import Base


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint(
            "entry_source IN ('paid', 'free')", name="entry_source_enum"
        ),
        CheckConstraint("ticket_number > 0", name="ticket_number_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    draw_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("draws.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    ticket_number: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_source: Mapped[str] = mapped_column(String, nullable=False)
    external_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
