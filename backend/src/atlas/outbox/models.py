"""Outbox ORM models (ADR-002 §Outbox table).

The table is defined here for Alembic; all inserts MUST go through
`atlas.outbox.writer.emit(...)`. Direct INSERT from other modules is
prohibited (grep-enforcement is a W9 story per week-8-build-plan §1
"Out of W8").
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from atlas.db import Base


class OutboxRow(Base):
    __tablename__ = "outbox"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_name: Mapped[str] = mapped_column(String, nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String, nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    last_error: Mapped[str | None] = mapped_column(String, nullable=True)
    next_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class OutboxDeadLetterRow(Base):
    """Terminal storage for events that exhausted their retry budget.

    Populated by the worker after `attempts >= outbox_max_attempts`.
    Operators inspect + replay per `docs/runbooks/outbox-dead-letter.md`.
    """

    __tablename__ = "outbox_dead_letter"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    original_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_name: Mapped[str] = mapped_column(String, nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String, nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    last_error: Mapped[str | None] = mapped_column(String, nullable=True)
    moved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
