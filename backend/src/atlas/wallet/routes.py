"""Wallet HTTP routes — read-only in V0.5.

Only the balance chip lands here; deposits and withdrawals are
demand-driven from the payment webhook (wallet.service.record_deposit)
rather than a direct wallet route. Withdrawals are V1.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.identity.auth import current_session
from atlas.identity.models import Session as SessionRow
from atlas.wallet import queries as wallet_queries
from atlas.wallet import service as wallet_service
from atlas.wallet.schemas import WalletBalance

router = APIRouter(prefix="/api/v1/users", tags=["wallet"])


@router.get(
    "/me/wallet",
    status_code=status.HTTP_200_OK,
    response_model=WalletBalance,
)
async def my_wallet_balance(
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
) -> WalletBalance:
    """Balance in kobo for the caller's user_wallet account.

    Lazy-creates the account row on first access — a user who has never
    received a deposit / prize / refund still gets a 200 response with
    balance_minor=0 rather than a 404. `updated_at` is the caller
    timestamp, not the timestamp of the last ledger entry — the balance
    is derived at read time so the two concepts don't overlap.
    """
    account = await wallet_service.get_or_create_user_wallet(
        db, user_id=session.user_id
    )
    balance = await wallet_queries.balance_of(db, account_id=account.id)
    await db.commit()
    return WalletBalance(
        balance_minor=balance,
        currency=account.currency,
        updated_at=datetime.now(UTC),
    )
