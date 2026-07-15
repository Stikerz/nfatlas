"""Read-only ledger queries.

`balance_of` returns the signed net balance in kobo — positive for accounts
that normally hold a credit balance (user_wallet, prize_pool), negative
for accounts that normally hold a debit balance from the operator's PoV.
Sign convention translation belongs in the service layer, not here.
"""

from __future__ import annotations

import uuid

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.wallet.models import LedgerEntry


async def balance_of(session: AsyncSession, *, account_id: uuid.UUID) -> int:
    """Return SUM(credit - debit) in kobo across all entries for the account."""
    signed_amount = case(
        (LedgerEntry.direction == "C", LedgerEntry.amount_minor),
        else_=-LedgerEntry.amount_minor,
    )
    result = await session.execute(
        select(func.coalesce(func.sum(signed_amount), 0)).where(
            LedgerEntry.account_id == account_id
        )
    )
    return int(result.scalar_one())
