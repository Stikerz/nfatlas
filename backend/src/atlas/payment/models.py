"""Payment ORM models (ADR-008 + migration 0005).

`PaymentIntent` here is the ORM row; the frozen dataclass with the same
name lives in `atlas.payment.providers.protocol` and represents the
adapter-boundary DTO. Downstream code refers to the ORM as
`PaymentIntentRow` where the two might be confused.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from atlas.db import Base


class PaymentIntentRow(Base):
    __tablename__ = "payment_intents"
    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="amount_positive"),
        CheckConstraint(
            "method IN ('card', 'bank_transfer', 'ussd', 'mobile_money')",
            name="method_enum",
        ),
        CheckConstraint(
            "status IN ('initiated', 'pending', 'succeeded', "
            "'failed', 'refunded', 'partially_refunded')",
            name="status_enum",
        ),
        CheckConstraint("vendor IN ('paystack')", name="vendor_enum"),
        Index("ix_payment_intents_user_id_created_at", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'NGN'"))
    method: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("'initiated'")
    )
    vendor: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'paystack'"))
    vendor_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    checkout_url: Mapped[str | None] = mapped_column(String, nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, server_default=text("''"))
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    raw_response: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
