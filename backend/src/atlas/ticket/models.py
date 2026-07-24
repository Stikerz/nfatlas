"""Ticket ORM models.

`tickets`: sole INSERT path is atlas.ticket.service._mint_ticket (grep-
enforced Day 5). `ticket_number` monotonic per draw — see service
module for the allocation concurrency contract.

`free_entry_slips`: sole INSERT path is atlas.ticket.service.issue_free
(Day 4). W5 Day 3 lands the ORM only.
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


class FreeEntrySlip(Base):
    __tablename__ = "free_entry_slips"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    draw_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("draws.id"), nullable=False
    )
    slip_reference: Mapped[str] = mapped_column(String, nullable=False)
    actor_operator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    subject_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
