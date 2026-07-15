"""Wallet & Ledger ORM models (ADR-003).

Two tables:

  ledger_accounts   — the chart of accounts. Types:
                      user_wallet | operator_revenue | prize_pool |
                      refund_payable | payment_gateway_clearing | tax_payable.
                      Operator-level rows have owner_id = NULL; user + draw +
                      gateway rows carry the owner identifier.

  ledger_entries    — the journal. Every INSERT goes through
                      atlas.wallet.ledger.post_transaction — CI grep enforces.
                      There is NO mutable `balance` column anywhere; balance is
                      always derived by atlas.wallet.queries.balance_of.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from atlas.db import Base


class LedgerAccount(Base):
    __tablename__ = "ledger_accounts"
    __table_args__ = (
        CheckConstraint(
            "account_type IN ("
            "'user_wallet', 'operator_revenue', 'prize_pool', "
            "'refund_payable', 'payment_gateway_clearing', 'tax_payable'"
            ")",
            name="account_type_enum",
        ),
        CheckConstraint(
            "owner_type IN ('user', 'operator', 'draw', 'gateway')",
            name="owner_type_enum",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    account_type: Mapped[str] = mapped_column(String, nullable=False)
    owner_type: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String, nullable=True)
    currency: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'NGN'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    __table_args__ = (
        CheckConstraint("direction IN ('D', 'C')", name="direction_enum"),
        CheckConstraint("amount_minor > 0", name="amount_positive"),
        Index("ix_ledger_entries_account_posted", "account_id", "posted_at"),
        Index("ix_ledger_entries_transaction", "transaction_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ledger_accounts.id"),
        nullable=False,
    )
    direction: Mapped[str] = mapped_column(String(1), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'NGN'"))
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    description: Mapped[str] = mapped_column(String, nullable=False)
    external_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
