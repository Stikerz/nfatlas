"""Payment service — orchestrates PaymentIntent rows and provider calls.

`create_intent` is the sole Week 4 entry point. It:
  1. Persists a `payment_intents` row with the client-supplied
     Idempotency-Key (unique constraint enforces one row per key).
  2. Calls `provider.create_intent(...)` to mint the vendor reference
     and checkout URL. Stub mode returns fixtures; live mode POSTs.
  3. Updates the row with `vendor_reference`, `checkout_url`, and the
     redacted raw response.
  4. Emits `payment.intent_created` on the audit log.

Idempotency-Key semantics on the endpoint are handled by
`atlas.idempotency.dependency.idempotency_guard` (ADR-004): same key +
same body → cached response; same key + different body → 409. The
`payment_intents.idempotency_key` UNIQUE index is defense in depth.

Payment intents have no explicit expiry; Paystack authorization URLs
are valid for ~30 minutes. We report `created_at + 30m` as an
informational hint; the vendor is the source of truth.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.payment.models import PaymentIntentRow
from atlas.payment.providers.paystack import PaystackAdapter
from atlas.payment.providers.protocol import (
    PaymentIntent,
    PaymentMethod,
    PaymentProvider,
    PaymentStatus,
    WebhookEvent,
)
from atlas.wallet import service as wallet_service

CHECKOUT_TTL = timedelta(minutes=30)

# Terminal states — a webhook that arrives after the intent already reached
# one of these is treated as a duplicate delivery and short-circuited.
_TERMINAL_STATUSES = frozenset(
    {
        PaymentStatus.SUCCEEDED.value,
        PaymentStatus.FAILED.value,
        PaymentStatus.REFUNDED.value,
        PaymentStatus.PARTIALLY_REFUNDED.value,
    }
)


def _default_provider() -> PaymentProvider:
    return PaystackAdapter()


async def create_intent(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    user_email: str,
    amount_minor: int,
    method: str,
    description: str,
    idempotency_key: str,
    provider: PaymentProvider | None = None,
) -> PaymentIntentRow:
    """Mint a new payment intent. Returns the persisted row.

    Caller owns the transaction (`await session.commit()` at the route).
    """
    prov = provider or _default_provider()

    row = PaymentIntentRow(
        user_id=user_id,
        amount_minor=amount_minor,
        currency="NGN",
        method=method,
        status=PaymentStatus.INITIATED.value,
        vendor=prov.name,
        idempotency_key=idempotency_key,
        description=description,
    )
    session.add(row)
    await session.flush()

    result = await prov.create_intent(
        PaymentIntent(
            user_id=str(user_id),
            amount_minor=amount_minor,
            currency="NGN",
            idempotency_key=idempotency_key,
            method=PaymentMethod(method),
            description=description,
            email=user_email,
            metadata={"payment_intent_id": str(row.id)},
        )
    )

    row.vendor_reference = result.vendor_reference
    row.checkout_url = result.checkout_url
    row.raw_response = result.raw_response_redacted
    row.status = result.status.value
    row.updated_at = datetime.now(UTC)
    await session.flush()

    await audit.append(
        session,
        actor_type="user",
        actor_id=str(user_id),
        event_name="payment.intent_created",
        subject_type="payment_intent",
        subject_id=str(row.id),
        payload={
            "user_id": str(user_id),
            "amount_minor": amount_minor,
            "method": method,
            "vendor": prov.name,
            "vendor_reference": result.vendor_reference,
        },
    )
    return row


def checkout_expires_at(row: PaymentIntentRow) -> datetime:
    return row.created_at + CHECKOUT_TTL


class UnknownVendorReferenceError(LookupError):
    """Webhook arrived for a vendor_reference we never issued."""


async def process_webhook_event(
    session: AsyncSession, *, event: WebhookEvent
) -> PaymentIntentRow | None:
    """Apply a verified webhook to the intent + wallet + audit log.

    Returns the updated intent row, or None if the event was for an
    unknown vendor_reference (Paystack sometimes sends events for
    references we didn't create — logged upstream, not raised).

    Idempotency: the intent's status guards against re-processing. If the
    intent is already in a terminal state, this is a no-op. Defense in
    depth: the ledger's `idempotency_key` UNIQUE index catches any
    second wallet-credit attempt even if the status guard is bypassed.

    Caller owns the transaction (`await session.commit()` at the route).
    """
    row = (
        await session.execute(
            select(PaymentIntentRow).where(
                PaymentIntentRow.vendor_reference == event.vendor_reference
            )
        )
    ).scalar_one_or_none()

    if row is None:
        return None

    if row.status in _TERMINAL_STATUSES:
        # Duplicate delivery for an already-processed intent.
        return row

    if event.status is PaymentStatus.SUCCEEDED:
        await _apply_succeeded(session, row=row, event=event)
    elif event.status is PaymentStatus.FAILED:
        await _apply_failed(session, row=row, event=event)
    else:
        # Any other status on a webhook (pending, refunded before we've
        # implemented refunds, etc.) is ignored for V0.5 — status stays
        # at whatever it was, no ledger side-effects.
        return row

    return row


async def _apply_succeeded(
    session: AsyncSession,
    *,
    row: PaymentIntentRow,
    event: WebhookEvent,
) -> None:
    row.status = PaymentStatus.SUCCEEDED.value
    row.updated_at = datetime.now(UTC)

    await wallet_service.record_deposit(
        session,
        user_id=row.user_id,
        amount_minor=event.amount_minor,
        external_ref=event.vendor_reference,
        idempotency_key=f"deposit:{event.vendor_reference}",
    )

    if event.fee_minor > 0:
        await wallet_service.record_payment_fee(
            session,
            vendor_reference=event.vendor_reference,
            amount_minor=event.fee_minor,
            idempotency_key=f"fee:{event.vendor_reference}",
        )

    await audit.append(
        session,
        actor_type="system",
        actor_id="payment.webhook",
        event_name="payment.confirmed",
        subject_type="payment_intent",
        subject_id=str(row.id),
        payload={
            "user_id": str(row.user_id),
            "amount_minor": event.amount_minor,
            "fee_minor": event.fee_minor,
            "vendor_reference": event.vendor_reference,
        },
    )


async def _apply_failed(
    session: AsyncSession,
    *,
    row: PaymentIntentRow,
    event: WebhookEvent,
) -> None:
    row.status = PaymentStatus.FAILED.value
    row.updated_at = datetime.now(UTC)

    await audit.append(
        session,
        actor_type="system",
        actor_id="payment.webhook",
        event_name="payment.failed",
        subject_type="payment_intent",
        subject_id=str(row.id),
        payload={
            "user_id": str(row.user_id),
            "amount_minor": event.amount_minor,
            "vendor_reference": event.vendor_reference,
        },
    )
