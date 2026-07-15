"""Ledger primitive — the sole INSERT path for `ledger_entries` (ADR-003).

Every wallet-service helper (record_deposit / record_ticket_purchase /
record_prize_award / record_refund) composes a list of `LedgerEntryDraft`
values and hands them to `post_transaction`. Direct INSERTs into
`ledger_entries` from any other module are grep-blocked in CI.

Balance enforcement: the deferred `ledger_transaction_balance` trigger
(migration 0004) checks at COMMIT that each transaction_id's sum of
credit-minus-debit equals zero. Unbalanced transactions raise on commit,
never on the individual INSERT — this lets the primitive add all sides
before validation runs.

Idempotency: ADR-003 §Schema puts a partial-unique index on
`idempotency_key WHERE idempotency_key IS NOT NULL`. To avoid conflicts
between the two-or-more entries of a single transaction, the key is set
on exactly one entry — the first one. On replay, we look up any entry
carrying that key; if found, we return its `transaction_id` (the
transaction already ran) and skip the INSERT entirely.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.wallet.models import LedgerEntry

Direction = Literal["D", "C"]


@dataclass(frozen=True)
class LedgerEntryDraft:
    """One side of a balanced transaction. Amounts are integer kobo (NGN minor)."""

    account_id: uuid.UUID
    direction: Direction
    amount_minor: int
    description: str
    external_ref: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.amount_minor <= 0:
            raise ValueError(
                f"amount_minor must be > 0 (got {self.amount_minor}); "
                "represent direction with the `direction` field, not sign."
            )
        if self.direction not in ("D", "C"):
            raise ValueError(f"direction must be 'D' or 'C' (got {self.direction!r})")


class UnbalancedTransactionError(ValueError):
    """Raised before INSERT if drafts don't balance to zero net."""


def _net_minor(entries: list[LedgerEntryDraft]) -> int:
    """Positive for net credit, negative for net debit. Balanced == 0."""
    return sum(
        e.amount_minor if e.direction == "C" else -e.amount_minor for e in entries
    )


async def post_transaction(
    session: AsyncSession,
    *,
    entries: list[LedgerEntryDraft],
    idempotency_key: str,
    external_ref: str | None = None,
) -> uuid.UUID:
    """Persist a balanced transaction. Returns the transaction_id.

    Application-side balance check runs first so unbalanced transactions
    fail with a typed error, not an opaque PG trigger exception. The DB
    trigger remains the source of truth at COMMIT.

    On idempotent replay (any existing row with this key), returns the
    existing transaction_id and skips the INSERT.
    """
    if len(entries) < 2:
        raise UnbalancedTransactionError(
            "a transaction needs at least two entries (debit + credit)"
        )

    net = _net_minor(entries)
    if net != 0:
        raise UnbalancedTransactionError(
            f"entries do not balance: net = {net} kobo"
        )

    existing = (
        await session.execute(
            select(LedgerEntry.transaction_id).where(
                LedgerEntry.idempotency_key == idempotency_key
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    transaction_id = uuid.uuid4()
    for index, draft in enumerate(entries):
        session.add(
            LedgerEntry(
                transaction_id=transaction_id,
                account_id=draft.account_id,
                direction=draft.direction,
                amount_minor=draft.amount_minor,
                description=draft.description,
                external_ref=draft.external_ref or external_ref,
                # The unique index tolerates NULL; carrying the key on the
                # first entry is enough for replay detection.
                idempotency_key=idempotency_key if index == 0 else None,
                metadata_=draft.metadata,
            )
        )
    await session.flush()
    return transaction_id
