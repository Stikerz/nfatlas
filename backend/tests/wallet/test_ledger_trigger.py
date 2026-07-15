"""Real-Postgres tests for the ledger primitive + deferred balance trigger.

Discipline per AINE-AGENTS.md §8.6: no mocks. The whole point of these
tests is to exercise the actual PL/pgSQL constraint trigger + the append-
only grants.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, InternalError
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.wallet.ledger import (
    LedgerEntryDraft,
    UnbalancedTransactionError,
    post_transaction,
)
from atlas.wallet.models import LedgerAccount, LedgerEntry
from atlas.wallet.queries import balance_of


async def _test_account(
    session: AsyncSession,
    *,
    account_type: str = "user_wallet",
    owner_type: str = "user",
    owner_id: str | None = None,
) -> uuid.UUID:
    account = LedgerAccount(
        account_type=account_type,
        owner_type=owner_type,
        owner_id=owner_id or str(uuid.uuid4()),
    )
    session.add(account)
    await session.flush()
    return account.id


async def test_seed_migration_lands_four_operator_accounts(
    db_session: AsyncSession,
) -> None:
    types = (
        await db_session.execute(
            select(LedgerAccount.account_type).where(LedgerAccount.owner_type != "user")
        )
    ).scalars().all()
    assert set(types) == {
        "operator_revenue",
        "refund_payable",
        "payment_gateway_clearing",
        "tax_payable",
    }


async def test_balanced_transaction_commits(db_session: AsyncSession) -> None:
    user_wallet = await _test_account(db_session, account_type="user_wallet")
    clearing = (
        await db_session.execute(
            select(LedgerAccount.id).where(
                LedgerAccount.account_type == "payment_gateway_clearing"
            )
        )
    ).scalar_one()

    tx_id = await post_transaction(
        db_session,
        entries=[
            LedgerEntryDraft(
                account_id=clearing,
                direction="D",
                amount_minor=500_00,
                description="Paystack test deposit — clearing debit",
            ),
            LedgerEntryDraft(
                account_id=user_wallet,
                direction="C",
                amount_minor=500_00,
                description="Paystack test deposit — user wallet credit",
            ),
        ],
        idempotency_key=str(uuid.uuid4()),
    )
    await db_session.commit()

    assert await balance_of(db_session, account_id=user_wallet) == 500_00
    assert await balance_of(db_session, account_id=clearing) == -500_00

    entries = (
        await db_session.execute(
            select(LedgerEntry).where(LedgerEntry.transaction_id == tx_id)
        )
    ).scalars().all()
    assert len(entries) == 2


async def test_unbalanced_transaction_rejected_by_app_precheck(
    db_session: AsyncSession,
) -> None:
    """Application catches unbalanced drafts BEFORE hitting the DB trigger."""
    a = await _test_account(db_session)
    b = await _test_account(db_session)

    with pytest.raises(UnbalancedTransactionError):
        await post_transaction(
            db_session,
            entries=[
                LedgerEntryDraft(
                    account_id=a, direction="D", amount_minor=500, description="d"
                ),
                LedgerEntryDraft(
                    account_id=b, direction="C", amount_minor=499, description="c"
                ),
            ],
            idempotency_key=str(uuid.uuid4()),
        )


async def test_deferred_trigger_rejects_direct_unbalanced_insert(
    db_session: AsyncSession,
) -> None:
    """Bypass the primitive and INSERT via raw SQL — trigger MUST reject on COMMIT."""
    a = await _test_account(db_session)
    tx_id = uuid.uuid4()

    await db_session.execute(
        text(
            "INSERT INTO ledger_entries "
            "(transaction_id, account_id, direction, amount_minor, description) "
            "VALUES (:tx, :acct, 'D', 100, 'unbalanced insert — no credit side')"
        ),
        {"tx": str(tx_id), "acct": str(a)},
    )

    with pytest.raises((IntegrityError, InternalError)) as exc_info:
        await db_session.commit()

    assert "unbalanced" in str(exc_info.value).lower()


async def test_contra_entry_reverses_a_prior_transaction(
    db_session: AsyncSession,
) -> None:
    a = await _test_account(db_session, account_type="user_wallet")
    # Use the seeded operator_revenue singleton so the test doesn't leak
    # a second operator_revenue row (which would survive cleanup).
    b = (
        await db_session.execute(
            select(LedgerAccount.id).where(
                LedgerAccount.account_type == "operator_revenue"
            )
        )
    ).scalar_one()

    await post_transaction(
        db_session,
        entries=[
            LedgerEntryDraft(account_id=b, direction="D", amount_minor=750, description="original D"),
            LedgerEntryDraft(account_id=a, direction="C", amount_minor=750, description="original C"),
        ],
        idempotency_key="tx-orig",
    )
    await db_session.commit()

    assert await balance_of(db_session, account_id=a) == 750

    await post_transaction(
        db_session,
        entries=[
            LedgerEntryDraft(account_id=a, direction="D", amount_minor=750, description="contra D"),
            LedgerEntryDraft(account_id=b, direction="C", amount_minor=750, description="contra C"),
        ],
        idempotency_key="tx-contra",
    )
    await db_session.commit()

    assert await balance_of(db_session, account_id=a) == 0
    assert await balance_of(db_session, account_id=b) == 0


async def test_idempotent_replay_returns_original_transaction_id(
    db_session: AsyncSession,
) -> None:
    a = await _test_account(db_session)
    b = await _test_account(db_session)
    key = f"replay-{uuid.uuid4()}"

    first = await post_transaction(
        db_session,
        entries=[
            LedgerEntryDraft(account_id=a, direction="D", amount_minor=100, description="d"),
            LedgerEntryDraft(account_id=b, direction="C", amount_minor=100, description="c"),
        ],
        idempotency_key=key,
    )
    await db_session.commit()

    second = await post_transaction(
        db_session,
        entries=[
            LedgerEntryDraft(account_id=a, direction="D", amount_minor=100, description="d"),
            LedgerEntryDraft(account_id=b, direction="C", amount_minor=100, description="c"),
        ],
        idempotency_key=key,
    )
    await db_session.commit()

    assert first == second

    count = (
        await db_session.execute(
            select(LedgerEntry).where(LedgerEntry.transaction_id == first)
        )
    ).scalars().all()
    assert len(count) == 2  # only one transaction ever inserted


async def test_single_entry_transaction_rejected(db_session: AsyncSession) -> None:
    a = await _test_account(db_session)
    with pytest.raises(UnbalancedTransactionError, match="at least two entries"):
        await post_transaction(
            db_session,
            entries=[
                LedgerEntryDraft(
                    account_id=a, direction="D", amount_minor=100, description="lone"
                ),
            ],
            idempotency_key=str(uuid.uuid4()),
        )


async def test_multi_side_balanced_transaction_commits(
    db_session: AsyncSession,
) -> None:
    """The 4-sided deposit+fee shape from ADR-008 §Fee handling."""
    user_wallet = await _test_account(db_session, account_type="user_wallet")
    clearing = (
        await db_session.execute(
            select(LedgerAccount.id).where(
                LedgerAccount.account_type == "payment_gateway_clearing"
            )
        )
    ).scalar_one()
    operator_revenue = (
        await db_session.execute(
            select(LedgerAccount.id).where(
                LedgerAccount.account_type == "operator_revenue"
            )
        )
    ).scalar_one()

    # Gross: 500 kobo user deposit; fee: 25 kobo.
    await post_transaction(
        db_session,
        entries=[
            LedgerEntryDraft(account_id=clearing, direction="D", amount_minor=500, description="gross D"),
            LedgerEntryDraft(account_id=user_wallet, direction="C", amount_minor=500, description="gross C"),
            LedgerEntryDraft(account_id=operator_revenue, direction="D", amount_minor=25, description="fee D"),
            LedgerEntryDraft(account_id=clearing, direction="C", amount_minor=25, description="fee C"),
        ],
        idempotency_key="deposit-with-fee",
    )
    await db_session.commit()

    assert await balance_of(db_session, account_id=user_wallet) == 500
    assert await balance_of(db_session, account_id=clearing) == -475
    assert await balance_of(db_session, account_id=operator_revenue) == -25
