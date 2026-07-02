# ADR-008: Payment vendor adapter abstraction (Paystack-first)

**Status:** Approved
**Date:** 2026-06-29
**Approved by:** S1408661 (Engineering Lead + Finance Lead, sole founder) on 2026-07-02
**Reversibility:** Two-way door for the adapter shape. Paystack-specific behaviour preserved behind the abstraction.

## Context

V1 ships Paystack only (`PRD.md §4`). The V2+ annex (`delivery-framework.md §11`) lists Flutterwave, Moniepoint, and USSD-direct as future rails. To avoid a rewrite at the first rail addition, V1 builds Payment through an adapter shape rather than calling Paystack SDK from route handlers.

## Decision

Define a `PaymentProvider` protocol in `backend/api/payment/providers/protocol.py` that all vendor adapters implement. Payment-module code calls the protocol.

### Protocol surface

```python
from typing import Protocol
from dataclasses import dataclass
from enum import Enum

class PaymentMethod(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    USSD = "ussd"                # V2+
    MOBILE_MONEY = "mobile_money" # V2+

class PaymentStatus(str, Enum):
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
    metadata: dict                  # not vendor-passed; for internal correlation

@dataclass(frozen=True)
class PaymentResult:
    status: PaymentStatus
    vendor_reference: str          # Paystack reference / equivalent
    checkout_url: str | None       # for redirect flows
    inline_token: str | None       # for inline checkout (mobile / web SDK)
    raw_response_redacted: dict
    created_at: str

@dataclass(frozen=True)
class WebhookEvent:
    vendor_reference: str
    status: PaymentStatus
    amount_minor: int
    currency: str
    raw_event_redacted: dict
    verified_at: str               # set after signature verification

class PaymentProvider(Protocol):
    name: str   # "paystack" | "flutterwave" | ...

    def create_intent(self, intent: PaymentIntent) -> PaymentResult: ...
    def fetch(self, vendor_reference: str) -> PaymentResult: ...
    def refund(self, vendor_reference: str, amount_minor: int, reason: str, idempotency_key: str) -> PaymentResult: ...
    def verify_webhook(self, raw_body: bytes, headers: dict) -> WebhookEvent: ...
```

### Webhook handling

- One webhook endpoint per vendor: `POST /api/v1/payments/webhooks/{vendor}`.
- The endpoint reads the raw body, calls `verify_webhook` on the matching provider, and only proceeds on signature pass.
- Verified events write to `audit_log` (`payment.confirmed`, `payment.failed`, `payment.refunded`) and to an outbox event for downstream consumers (Wallet credit, Ticket issuance).
- Webhook handlers are idempotent via the `vendor_reference` + `payment_intents` row state.

### Settlement reconciliation

A nightly job (`backend/api/payment/jobs/reconcile.py`, owned by Backend Engineer):

1. Fetches Paystack settlement report for the prior day.
2. Sums credits to `payment_gateway_clearing` (ADR-003) for that day.
3. Compares; difference beyond tolerance triggers SEV-1 + Compliance & Risk review per `docs/qa/strategy.md` tolerance threshold.

### Fee handling

Paystack fees are recorded as a separate ledger entry from the user payment:
- Debit: `payment_gateway_clearing`, credit: `user_wallet` for the gross amount.
- Debit: `operator_revenue` (negative), credit: `payment_gateway_clearing` for the fee.

This keeps the user's deposit history clean and the operator's fee cost separately visible.

## Alternatives considered

- **Paystack SDK called directly from route handlers.** Lost: every future rail becomes a rewrite. Adapter cost is negligible.
- **A single "payments aggregator" vendor (e.g. Stripe-like multi-rail provider).** Lost: no equivalent with the rail coverage Atlas needs in Nigeria; aggregators that exist add latency and another fee layer.
- **Asynchronous-first design** (every payment is an intent + webhook with no synchronous success path). Considered: matches BANK_TRANSFER semantics but is worse UX for CARD (which often returns success synchronously). The adapter supports both per-method.

## Consequences

**Positive:**
- Adding Flutterwave / Moniepoint in V2 is implementing the protocol + a router config update.
- Webhook signature verification is mandatory and isolated; tampering attempts are caught at the adapter boundary.
- Fee separation makes financial reporting straightforward.

**Negative:**
- Vendor-specific features (e.g. Paystack's recurring-billing primitives) require protocol extension when used. V1 doesn't use them (subscriptions are V2+).
- Two-source-of-truth risk: payment intent state in our DB vs vendor's state. Mitigated by reconciliation job + `fetch` calls when a webhook is delayed.
- Two-approval gate on every Payment PR slows iteration. Accepted — payments are irreversible.

**Invariants:**
- All payment-vendor calls go through the adapter; no direct SDK imports in `backend/api/payment/` outside the adapter implementation. Enforced by CI grep.
- Webhook endpoints reject any request that fails signature verification with 401; no body parsing happens before verification.
- Reconciliation job runs nightly from Phase 3 onwards.
- Every payment-state change emits an outbox event (ADR-002) and an audit-log entry (ADR-005).
