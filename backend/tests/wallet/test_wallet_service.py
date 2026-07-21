"""Integration tests for atlas.wallet.service (real Postgres).

Covers the four Day 2 helpers + get_or_create + audit-event integration.
"""

from __future__ import annotations

import itertools
import uuid
from datetime import date

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog
from atlas.config import Settings
from atlas.identity.models import User
from atlas.wallet import service as wallet
from atlas.wallet.models import LedgerAccount
from atlas.wallet.queries import balance_of


async def _make_user(session: AsyncSession) -> uuid.UUID:
    user = User(
        email=f"kemi-{uuid.uuid4().hex[:8]}@example.com",
        phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
        date_of_birth=date(1993, 3, 12),
        status="active",
    )
    session.add(user)
    await session.flush()
    return user.id


class TestGetOrCreate:
    async def test_user_wallet_created_first_time(self, db_session: AsyncSession) -> None:
        user_id = await _make_user(db_session)
        wallet_account = await wallet.get_or_create_user_wallet(
            db_session, user_id=user_id
        )
        assert wallet_account.account_type == "user_wallet"
        assert wallet_account.owner_type == "user"
        assert wallet_account.owner_id == str(user_id)

    async def test_user_wallet_idempotent(self, db_session: AsyncSession) -> None:
        user_id = await _make_user(db_session)
        first = await wallet.get_or_create_user_wallet(db_session, user_id=user_id)
        second = await wallet.get_or_create_user_wallet(db_session, user_id=user_id)
        assert first.id == second.id

        count = (
            await db_session.execute(
                select(func.count())
                .select_from(LedgerAccount)
                .where(LedgerAccount.owner_id == str(user_id))
            )
        ).scalar_one()
        assert count == 1

    async def test_prize_pool_isolated_per_draw(
        self, db_session: AsyncSession
    ) -> None:
        pool_a = await wallet.get_or_create_prize_pool(db_session, draw_id="draw-alpha")
        pool_b = await wallet.get_or_create_prize_pool(db_session, draw_id="draw-beta")
        assert pool_a.id != pool_b.id


class TestRecordDeposit:
    async def test_credits_wallet_and_debits_clearing(
        self, db_session: AsyncSession
    ) -> None:
        user_id = await _make_user(db_session)
        tx_id = await wallet.record_deposit(
            db_session,
            user_id=user_id,
            amount_minor=500_00,
            external_ref="paystack-ref-abc",
            idempotency_key=f"deposit-{uuid.uuid4()}",
        )
        await db_session.commit()
        assert isinstance(tx_id, uuid.UUID)

        user_wallet = await wallet.get_or_create_user_wallet(db_session, user_id=user_id)
        clearing = (
            await db_session.execute(
                select(LedgerAccount).where(
                    LedgerAccount.account_type == "payment_gateway_clearing"
                )
            )
        ).scalar_one()

        assert await balance_of(db_session, account_id=user_wallet.id) == 500_00
        assert await balance_of(db_session, account_id=clearing.id) == -500_00

    async def test_emits_deposit_credited_audit_event(
        self, db_session: AsyncSession
    ) -> None:
        user_id = await _make_user(db_session)
        await wallet.record_deposit(
            db_session,
            user_id=user_id,
            amount_minor=250_00,
            external_ref="paystack-ref-xyz",
            idempotency_key=f"deposit-{uuid.uuid4()}",
        )
        await db_session.commit()

        event = (
            await db_session.execute(
                select(AuditLog).where(
                    AuditLog.event_name == "wallet.deposit_credited"
                )
            )
        ).scalar_one()
        assert event.payload["amount_minor"] == 250_00
        assert event.payload["external_ref"] == "paystack-ref-xyz"

    async def test_idempotent_replay_no_duplicate_credit(
        self, db_session: AsyncSession
    ) -> None:
        user_id = await _make_user(db_session)
        key = f"deposit-{uuid.uuid4()}"

        first = await wallet.record_deposit(
            db_session,
            user_id=user_id,
            amount_minor=100_00,
            external_ref="ref-1",
            idempotency_key=key,
        )
        await db_session.commit()

        second = await wallet.record_deposit(
            db_session,
            user_id=user_id,
            amount_minor=100_00,
            external_ref="ref-1",
            idempotency_key=key,
        )
        await db_session.commit()

        assert first == second
        user_wallet = await wallet.get_or_create_user_wallet(db_session, user_id=user_id)
        assert await balance_of(db_session, account_id=user_wallet.id) == 100_00


class TestRecordTicketPurchase:
    async def test_debits_wallet_and_credits_prize_pool(
        self, db_session: AsyncSession
    ) -> None:
        user_id = await _make_user(db_session)
        # Fund the wallet first so the purchase has money to debit.
        await wallet.record_deposit(
            db_session,
            user_id=user_id,
            amount_minor=1_000_00,
            external_ref="seed-funding",
            idempotency_key=f"seed-{uuid.uuid4()}",
        )
        await db_session.commit()

        await wallet.record_ticket_purchase(
            db_session,
            user_id=user_id,
            draw_id="stub-draw-1",
            amount_minor=100_00,
            idempotency_key=f"purchase-{uuid.uuid4()}",
        )
        await db_session.commit()

        user_wallet = await wallet.get_or_create_user_wallet(db_session, user_id=user_id)
        prize_pool = await wallet.get_or_create_prize_pool(
            db_session, draw_id="stub-draw-1"
        )
        assert await balance_of(db_session, account_id=user_wallet.id) == 900_00
        assert await balance_of(db_session, account_id=prize_pool.id) == 100_00

    async def test_stub_flag_off_blocks_purchase(
        self, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Swap the cached settings with a version that has the flag off.
        original = Settings(wallet_allow_stub_draw=False)  # type: ignore[call-arg]
        monkeypatch.setattr("atlas.wallet.service.get_settings", lambda: original)

        user_id = await _make_user(db_session)
        with pytest.raises(wallet.StubDrawDisabledError):
            await wallet.record_ticket_purchase(
                db_session,
                user_id=user_id,
                draw_id="stub-draw-2",
                amount_minor=100,
                idempotency_key=f"blocked-{uuid.uuid4()}",
            )


class TestRecordPrizeAward:
    async def test_debits_prize_pool_and_credits_winner_wallet(
        self, db_session: AsyncSession
    ) -> None:
        # Fund a prize pool via a ticket purchase from user A, then award to user B.
        user_a = await _make_user(db_session)
        user_b = await _make_user(db_session)

        await wallet.record_deposit(
            db_session,
            user_id=user_a,
            amount_minor=500_00,
            external_ref="seed",
            idempotency_key=f"seed-{uuid.uuid4()}",
        )
        await db_session.commit()

        await wallet.record_ticket_purchase(
            db_session,
            user_id=user_a,
            draw_id="draw-award-1",
            amount_minor=500_00,
            idempotency_key=f"buy-{uuid.uuid4()}",
        )
        await db_session.commit()

        await wallet.record_prize_award(
            db_session,
            user_id=user_b,
            draw_id="draw-award-1",
            amount_minor=500_00,
            idempotency_key=f"award-{uuid.uuid4()}",
        )
        await db_session.commit()

        winner_wallet = await wallet.get_or_create_user_wallet(db_session, user_id=user_b)
        prize_pool = await wallet.get_or_create_prize_pool(
            db_session, draw_id="draw-award-1"
        )
        assert await balance_of(db_session, account_id=winner_wallet.id) == 500_00
        assert await balance_of(db_session, account_id=prize_pool.id) == 0


class TestRecordRefund:
    async def test_credits_wallet_and_debits_refund_payable(
        self, db_session: AsyncSession
    ) -> None:
        user_id = await _make_user(db_session)
        await wallet.record_refund(
            db_session,
            user_id=user_id,
            amount_minor=250_00,
            reason="duplicate charge",
            idempotency_key=f"refund-{uuid.uuid4()}",
        )
        await db_session.commit()

        user_wallet = await wallet.get_or_create_user_wallet(db_session, user_id=user_id)
        refund_payable = (
            await db_session.execute(
                select(LedgerAccount).where(
                    LedgerAccount.account_type == "refund_payable"
                )
            )
        ).scalar_one()
        assert await balance_of(db_session, account_id=user_wallet.id) == 250_00
        assert await balance_of(db_session, account_id=refund_payable.id) == -250_00


class TestAuditChainIntegrity:
    async def test_deposit_then_purchase_then_award_chain_intact(
        self, db_session: AsyncSession
    ) -> None:
        user_id = await _make_user(db_session)

        await wallet.record_deposit(
            db_session,
            user_id=user_id,
            amount_minor=1_000_00,
            external_ref="ref-1",
            idempotency_key=f"d-{uuid.uuid4()}",
        )
        await db_session.commit()

        await wallet.record_ticket_purchase(
            db_session,
            user_id=user_id,
            draw_id="chain-draw",
            amount_minor=500_00,
            idempotency_key=f"tp-{uuid.uuid4()}",
        )
        await db_session.commit()

        await wallet.record_prize_award(
            db_session,
            user_id=user_id,
            draw_id="chain-draw",
            amount_minor=500_00,
            idempotency_key=f"pa-{uuid.uuid4()}",
        )
        await db_session.commit()

        events = (
            await db_session.execute(
                select(AuditLog)
                .where(
                    AuditLog.event_name.in_(
                        [
                            "wallet.deposit_credited",
                            "wallet.ticket_purchase_posted",
                            "wallet.prize_awarded",
                        ]
                    )
                )
                .order_by(AuditLog.seq)
            )
        ).scalars().all()

        assert len(events) == 3
        for prev, curr in itertools.pairwise(events):
            assert curr.prev_hash == prev.row_hash
