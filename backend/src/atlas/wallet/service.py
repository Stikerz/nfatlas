"""Wallet service — domain helpers that compose balanced ledger transactions.

The four operations V0.5 needs:
  record_deposit          Paystack webhook → user_wallet credit.
  record_ticket_purchase  User buys a ticket (Week 5 wires the real draw;
                          gated behind ATLAS_WALLET_ALLOW_STUB_DRAW today).
  record_prize_award      Draw pays out to the winner.
  record_refund           Payout of a previously-booked refund liability.

Each helper produces a balanced transaction via `atlas.wallet.ledger.
post_transaction` and emits a matching audit event via `atlas.audit_log.
writer.append`. Callers own commit/rollback.

Sign conventions:
  user_wallet             normal credit balance (money owed to user).
  operator_revenue        normal credit balance (income).
  prize_pool              normal credit balance (funds reserved to pay out).
  refund_payable          normal credit balance (liability to refund users).
  payment_gateway_clearing normal debit balance (money in flight from user
                          to operator; positive means gateway owes us).
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.config import get_settings
from atlas.wallet.ledger import LedgerEntryDraft, post_transaction
from atlas.wallet.models import LedgerAccount

GATEWAY_PAYSTACK = "paystack"


class StubDrawDisabledError(RuntimeError):
    """Raised when record_ticket_purchase runs with WALLET_ALLOW_STUB_DRAW=false.

    In V0.5 the flag is true so Week 4 can exercise the full transaction
    shape before the ticket + draw modules land Week 5.
    """


async def get_or_create_user_wallet(
    session: AsyncSession, *, user_id: uuid.UUID
) -> LedgerAccount:
    """Return the user's wallet account, creating it on first access."""
    return await _get_or_create_account(
        session,
        account_type="user_wallet",
        owner_type="user",
        owner_id=str(user_id),
    )


async def get_or_create_prize_pool(
    session: AsyncSession, *, draw_id: str
) -> LedgerAccount:
    """Return the prize-pool account for a draw, creating it on first access."""
    return await _get_or_create_account(
        session,
        account_type="prize_pool",
        owner_type="draw",
        owner_id=draw_id,
    )


async def _get_or_create_account(
    session: AsyncSession,
    *,
    account_type: str,
    owner_type: str,
    owner_id: str,
    currency: str = "NGN",
) -> LedgerAccount:
    """Race-safe insert-or-fetch via ON CONFLICT DO NOTHING + SELECT.

    The UNIQUE NULLS NOT DISTINCT constraint on ledger_accounts is the
    real guard; ON CONFLICT DO NOTHING just tells Postgres to swallow the
    duplicate error so the follow-up SELECT can pick up the winning row.
    """
    stmt = (
        pg_insert(LedgerAccount)
        .values(
            account_type=account_type,
            owner_type=owner_type,
            owner_id=owner_id,
            currency=currency,
        )
        .on_conflict_do_nothing(
            constraint="uq_ledger_accounts_identity",
        )
    )
    await session.execute(stmt)
    row = (
        await session.execute(
            select(LedgerAccount).where(
                LedgerAccount.account_type == account_type,
                LedgerAccount.owner_type == owner_type,
                LedgerAccount.owner_id == owner_id,
                LedgerAccount.currency == currency,
            )
        )
    ).scalar_one()
    return row


async def _get_operator_account(
    session: AsyncSession,
    *,
    account_type: str,
    gateway_id: str | None = None,
) -> LedgerAccount:
    """Fetch a seed operator-level singleton. Missing = migration didn't run."""
    stmt = select(LedgerAccount).where(LedgerAccount.account_type == account_type)
    if gateway_id is not None:
        stmt = stmt.where(LedgerAccount.owner_id == gateway_id)
    return (await session.execute(stmt)).scalar_one()


async def record_deposit(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    amount_minor: int,
    external_ref: str,
    idempotency_key: str,
) -> uuid.UUID:
    """User deposit landed via payment webhook. Credits user_wallet, debits
    payment_gateway_clearing (Paystack)."""
    user_wallet = await get_or_create_user_wallet(session, user_id=user_id)
    clearing = await _get_operator_account(
        session,
        account_type="payment_gateway_clearing",
        gateway_id=GATEWAY_PAYSTACK,
    )

    tx_id = await post_transaction(
        session,
        entries=[
            LedgerEntryDraft(
                account_id=clearing.id,
                direction="D",
                amount_minor=amount_minor,
                description="Deposit landed — payment_gateway_clearing debit",
                external_ref=external_ref,
            ),
            LedgerEntryDraft(
                account_id=user_wallet.id,
                direction="C",
                amount_minor=amount_minor,
                description="Deposit landed — user_wallet credit",
                external_ref=external_ref,
            ),
        ],
        idempotency_key=idempotency_key,
        external_ref=external_ref,
    )

    await audit.append(
        session,
        actor_type="system",
        actor_id="payment.webhook",
        event_name="wallet.deposit_credited",
        subject_type="user",
        subject_id=str(user_id),
        payload={
            "user_id": str(user_id),
            "amount_minor": amount_minor,
            "transaction_id": str(tx_id),
            "external_ref": external_ref,
        },
    )
    return tx_id


async def record_ticket_purchase(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    draw_id: str,
    amount_minor: int,
    idempotency_key: str,
) -> uuid.UUID:
    """User buys a ticket. Debits user_wallet, credits prize_pool for the draw.

    Blocked in production unless a real draw exists (V0.5 stub gate).
    """
    if not get_settings().wallet_allow_stub_draw:
        # V1 semantics: verify the draw is real (Week 5 wires the check
        # against atlas.draw when that module lands).
        raise StubDrawDisabledError(
            "record_ticket_purchase requires a real draw; "
            "the WALLET_ALLOW_STUB_DRAW flag is off."
        )

    user_wallet = await get_or_create_user_wallet(session, user_id=user_id)
    prize_pool = await get_or_create_prize_pool(session, draw_id=draw_id)

    tx_id = await post_transaction(
        session,
        entries=[
            LedgerEntryDraft(
                account_id=user_wallet.id,
                direction="D",
                amount_minor=amount_minor,
                description=f"Ticket purchase — draw {draw_id}",
            ),
            LedgerEntryDraft(
                account_id=prize_pool.id,
                direction="C",
                amount_minor=amount_minor,
                description=f"Ticket purchase — prize_pool for draw {draw_id}",
            ),
        ],
        idempotency_key=idempotency_key,
    )

    await audit.append(
        session,
        actor_type="user",
        actor_id=str(user_id),
        event_name="wallet.ticket_purchase_posted",
        subject_type="user",
        subject_id=str(user_id),
        payload={
            "user_id": str(user_id),
            "draw_id": draw_id,
            "amount_minor": amount_minor,
            "transaction_id": str(tx_id),
        },
    )
    return tx_id


async def record_prize_award(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    draw_id: str,
    amount_minor: int,
    idempotency_key: str,
) -> uuid.UUID:
    """Draw awards a prize. Debits prize_pool, credits winner's user_wallet."""
    user_wallet = await get_or_create_user_wallet(session, user_id=user_id)
    prize_pool = await get_or_create_prize_pool(session, draw_id=draw_id)

    tx_id = await post_transaction(
        session,
        entries=[
            LedgerEntryDraft(
                account_id=prize_pool.id,
                direction="D",
                amount_minor=amount_minor,
                description=f"Prize award — prize_pool debit for draw {draw_id}",
            ),
            LedgerEntryDraft(
                account_id=user_wallet.id,
                direction="C",
                amount_minor=amount_minor,
                description="Prize award — winner user_wallet credit",
            ),
        ],
        idempotency_key=idempotency_key,
    )

    await audit.append(
        session,
        actor_type="system",
        actor_id="draw.engine",
        event_name="wallet.prize_awarded",
        subject_type="user",
        subject_id=str(user_id),
        payload={
            "user_id": str(user_id),
            "draw_id": draw_id,
            "amount_minor": amount_minor,
            "transaction_id": str(tx_id),
        },
    )
    return tx_id


async def record_ticket_sale(
    session: AsyncSession,
    *,
    amount_minor: int,
    external_ref: str,
    idempotency_key: str,
) -> uuid.UUID:
    """Direct-to-Paystack ticket-purchase deposit-side per week-5-build-
    plan §0 ask 1.

    Debit  payment_gateway_clearing (money in flight from user to us)
    Credit operator_revenue          (ticket-sale income)

    Distinct from record_deposit — this path never touches user_wallet
    because V0.5 users don't deposit-to-wallet-then-buy. The fee side
    posts separately via record_payment_fee (same shape as W4).
    """
    operator_revenue = await _get_operator_account(
        session, account_type="operator_revenue"
    )
    clearing = await _get_operator_account(
        session,
        account_type="payment_gateway_clearing",
        gateway_id=GATEWAY_PAYSTACK,
    )

    tx_id = await post_transaction(
        session,
        entries=[
            LedgerEntryDraft(
                account_id=clearing.id,
                direction="D",
                amount_minor=amount_minor,
                description=f"Ticket sale — payment_gateway_clearing debit for {external_ref}",
                external_ref=external_ref,
            ),
            LedgerEntryDraft(
                account_id=operator_revenue.id,
                direction="C",
                amount_minor=amount_minor,
                description=f"Ticket sale — operator_revenue for {external_ref}",
                external_ref=external_ref,
            ),
        ],
        idempotency_key=idempotency_key,
        external_ref=external_ref,
    )

    await audit.append(
        session,
        actor_type="system",
        actor_id="payment.webhook",
        event_name="wallet.ticket_sale_recorded",
        subject_type="gateway",
        subject_id=GATEWAY_PAYSTACK,
        payload={
            "amount_minor": amount_minor,
            "external_ref": external_ref,
            "transaction_id": str(tx_id),
        },
    )
    return tx_id


async def record_payment_fee(
    session: AsyncSession,
    *,
    vendor_reference: str,
    amount_minor: int,
    idempotency_key: str,
) -> uuid.UUID:
    """Paystack fee posting per ADR-008 §Fee handling.

    Recorded as a SEPARATE transaction from the deposit so the user's
    deposit history stays clean and the operator's fee cost is visible
    on its own line.

    Debit  operator_revenue        (reduces income by the fee cost)
    Credit payment_gateway_clearing (reduces the amount Paystack owes us,
                                     since they netted the fee before
                                     settlement)
    """
    operator_revenue = await _get_operator_account(
        session, account_type="operator_revenue"
    )
    clearing = await _get_operator_account(
        session,
        account_type="payment_gateway_clearing",
        gateway_id=GATEWAY_PAYSTACK,
    )

    tx_id = await post_transaction(
        session,
        entries=[
            LedgerEntryDraft(
                account_id=operator_revenue.id,
                direction="D",
                amount_minor=amount_minor,
                description=f"Paystack fee — vendor_ref {vendor_reference}",
                external_ref=vendor_reference,
            ),
            LedgerEntryDraft(
                account_id=clearing.id,
                direction="C",
                amount_minor=amount_minor,
                description=f"Paystack fee — clearing offset for {vendor_reference}",
                external_ref=vendor_reference,
            ),
        ],
        idempotency_key=idempotency_key,
        external_ref=vendor_reference,
    )

    await audit.append(
        session,
        actor_type="system",
        actor_id="payment.webhook",
        event_name="wallet.payment_fee_posted",
        subject_type="gateway",
        subject_id=GATEWAY_PAYSTACK,
        payload={
            "vendor_reference": vendor_reference,
            "amount_minor": amount_minor,
            "transaction_id": str(tx_id),
        },
    )
    return tx_id


async def record_refund(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    amount_minor: int,
    reason: str,
    idempotency_key: str,
) -> uuid.UUID:
    """Refund payout — debits refund_payable, credits user_wallet.

    Presumes the refund_payable liability was booked by an earlier operator
    action (Week 5+ admin surface). V0.5 fires this only from the admin
    seed-tools panel for demo purposes.
    """
    user_wallet = await get_or_create_user_wallet(session, user_id=user_id)
    refund_payable = await _get_operator_account(
        session, account_type="refund_payable"
    )

    tx_id = await post_transaction(
        session,
        entries=[
            LedgerEntryDraft(
                account_id=refund_payable.id,
                direction="D",
                amount_minor=amount_minor,
                description=f"Refund payout — {reason}",
            ),
            LedgerEntryDraft(
                account_id=user_wallet.id,
                direction="C",
                amount_minor=amount_minor,
                description=f"Refund credit — {reason}",
            ),
        ],
        idempotency_key=idempotency_key,
    )

    await audit.append(
        session,
        actor_type="operator",
        actor_id="refund.issued",
        event_name="wallet.refund_issued",
        subject_type="user",
        subject_id=str(user_id),
        payload={
            "user_id": str(user_id),
            "amount_minor": amount_minor,
            "reason": reason,
            "transaction_id": str(tx_id),
        },
    )
    return tx_id
