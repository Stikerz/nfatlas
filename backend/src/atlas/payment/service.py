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

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.payment.models import PaymentIntentRow
from atlas.payment.providers.paystack import PaystackAdapter
from atlas.payment.providers.protocol import (
    PaymentIntent,
    PaymentMethod,
    PaymentProvider,
    PaymentStatus,
)

CHECKOUT_TTL = timedelta(minutes=30)


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
