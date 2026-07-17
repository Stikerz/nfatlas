"""Payment provider protocol per ADR-008 §Protocol surface.

Payment-module callers depend on `PaymentProvider`, never on a concrete
vendor. `create_intent`, `fetch`, `refund` and `verify_webhook` are the
four operations V1 uses. The dataclasses are frozen so a vendor cannot
mutate what it was handed and so results are hashable for logging.

Note on async: ADR-008's original signatures are synchronous. Our stack
is async end-to-end (FastAPI + asyncpg + httpx), so the protocol methods
are async here. This is a pure implementation choice — the abstraction
is unchanged and swapping a vendor still means implementing this
protocol.

Note on `raw_response_redacted` / `raw_event_redacted`: adapters MUST
strip authorization codes, card-number fragments, CVVs, and any field
that could regenerate a PAN before returning. The redacted payload is
what gets persisted to `payment_intents.raw_response` and — for
webhooks — passed to downstream handlers. See ADR-008 §Consequences.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class PaymentMethod(StrEnum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    USSD = "ussd"                # V2+
    MOBILE_MONEY = "mobile_money"  # V2+


class PaymentStatus(StrEnum):
    INITIATED = "initiated"        # intent created at vendor
    PENDING = "pending"            # awaiting user / awaiting webhook
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


@dataclass(frozen=True)
class PaymentIntent:
    user_id: str
    amount_minor: int              # kobo
    currency: str                  # "NGN"
    idempotency_key: str           # client-supplied per ADR-004
    method: PaymentMethod
    description: str
    email: str                     # vendor requires an email for the checkout page
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PaymentResult:
    status: PaymentStatus
    vendor_reference: str          # Paystack reference / equivalent
    checkout_url: str | None       # for redirect flows
    inline_token: str | None       # for inline checkout (mobile / web SDK)
    fee_minor: int                 # vendor-reported fee in kobo (0 until known)
    raw_response_redacted: dict[str, Any]
    created_at: str                # ISO-8601 UTC


@dataclass(frozen=True)
class WebhookEvent:
    vendor_reference: str
    status: PaymentStatus
    amount_minor: int
    currency: str
    fee_minor: int                 # from the event payload, if present
    raw_event_redacted: dict[str, Any]
    verified_at: str               # ISO-8601 UTC, set after signature verification


class InvalidSignatureError(Exception):
    """Raised by verify_webhook when a signature does not match the raw body."""


class PaymentProvider(Protocol):
    name: str   # "paystack" | "flutterwave" | ...

    async def create_intent(self, intent: PaymentIntent) -> PaymentResult: ...

    async def fetch(self, vendor_reference: str) -> PaymentResult: ...

    async def refund(
        self,
        vendor_reference: str,
        amount_minor: int,
        reason: str,
        idempotency_key: str,
    ) -> PaymentResult: ...

    def verify_webhook(
        self, raw_body: bytes, headers: dict[str, str]
    ) -> WebhookEvent: ...
