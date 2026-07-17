"""Paystack adapter (ADR-008).

Two operating modes, gated by `ATLAS_PAYSTACK_STUB_MODE`:

  stub mode (V0.5 default)   short-circuits every network call to
                             `paystack_fixtures.*` — no HTTP goes out.
  live mode (Week 5+)        POSTs to https://api.paystack.co with the
                             secret key in the Authorization header.

Both modes exercise the same code path through `_persist_result` so a
mode flip does not change downstream behaviour. `verify_webhook` runs
the real HMAC-SHA-512 path in both modes — Day 4's tests generate
signatures with the same webhook secret the handler verifies against.

Reference generation: derived from the client's idempotency_key
(`atlas-<sha256[:24]>`) so a retry with the same key produces the same
vendor reference. Paystack itself deduplicates by reference.

Redaction: fields whose combination could reconstruct card data — the
`authorization` block's `authorization_code`, `bin`, `last4`, `signature`
— are stripped before the response is persisted. Channel + bank stay
because reconciliation needs them.
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime
from typing import Any

import httpx

from atlas.config import get_settings
from atlas.payment.providers import paystack_fixtures
from atlas.payment.providers.protocol import (
    InvalidSignatureError,
    PaymentIntent,
    PaymentResult,
    PaymentStatus,
    WebhookEvent,
)

PAYSTACK_API_BASE = "https://api.paystack.co"
_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
_REDACT_KEYS = frozenset(
    {"authorization_code", "bin", "last4", "signature", "card_type"}
)


def _reference_for(idempotency_key: str) -> str:
    digest = hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()[:24]
    return f"atlas-{digest}"


def _iso_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


def _redact(payload: Any) -> Any:
    """Deep-copy `payload` with sensitive keys stripped. Idempotent."""
    if isinstance(payload, dict):
        return {k: _redact(v) for k, v in payload.items() if k not in _REDACT_KEYS}
    if isinstance(payload, list):
        return [_redact(v) for v in payload]
    return payload


class PaystackAdapter:
    """Implements `atlas.payment.providers.protocol.PaymentProvider`."""

    name = "paystack"

    def __init__(self, *, stub_mode: bool | None = None) -> None:
        settings = get_settings()
        self._stub_mode = settings.paystack_stub_mode if stub_mode is None else stub_mode
        self._secret_key: str | None = (
            settings.paystack_secret_key.get_secret_value()
            if settings.paystack_secret_key is not None
            else None
        )
        self._webhook_secret: str = settings.paystack_webhook_secret.get_secret_value()

    # ── create_intent ────────────────────────────────────────────────────
    async def create_intent(self, intent: PaymentIntent) -> PaymentResult:
        reference = _reference_for(intent.idempotency_key)
        if self._stub_mode:
            raw = paystack_fixtures.initialize_response(
                reference=reference,
                amount_minor=intent.amount_minor,
                email=intent.email,
            )
        else:
            raw = await self._post(
                "/transaction/initialize",
                json={
                    "email": intent.email,
                    "amount": intent.amount_minor,
                    "currency": intent.currency,
                    "reference": reference,
                    "metadata": {
                        "user_id": intent.user_id,
                        "idempotency_key": intent.idempotency_key,
                        "description": intent.description,
                        **intent.metadata,
                    },
                },
            )
        data = raw.get("data", {})
        return PaymentResult(
            status=PaymentStatus.INITIATED,
            vendor_reference=data.get("reference", reference),
            checkout_url=data.get("authorization_url"),
            inline_token=data.get("access_code"),
            fee_minor=0,  # not known until charge.success webhook
            raw_response_redacted=_redact(raw),
            created_at=_iso_now(),
        )

    # ── fetch ────────────────────────────────────────────────────────────
    async def fetch(self, vendor_reference: str) -> PaymentResult:
        if self._stub_mode:
            raw = paystack_fixtures.verify_success_response(
                reference=vendor_reference,
                amount_minor=0,
                email="stub@example.com",
            )
        else:
            raw = await self._get(f"/transaction/verify/{vendor_reference}")
        data = raw.get("data", {})
        status = self._map_status(data.get("status", "pending"))
        return PaymentResult(
            status=status,
            vendor_reference=data.get("reference", vendor_reference),
            checkout_url=None,
            inline_token=None,
            fee_minor=int(data.get("fees") or 0),
            raw_response_redacted=_redact(raw),
            created_at=_iso_now(),
        )

    # ── refund (V1) ──────────────────────────────────────────────────────
    async def refund(
        self,
        vendor_reference: str,
        amount_minor: int,
        reason: str,
        idempotency_key: str,
    ) -> PaymentResult:
        # V1 refunds land Week 5+; wire the surface so the protocol is
        # satisfied, but keep the live path unimplemented.
        raise NotImplementedError(
            "PaystackAdapter.refund is a Week 5+ ticket; see week-4-build-plan §1 Out."
        )

    # ── verify_webhook ───────────────────────────────────────────────────
    def verify_webhook(
        self, raw_body: bytes, headers: dict[str, str]
    ) -> WebhookEvent:
        signature = headers.get("x-paystack-signature") or headers.get(
            "X-Paystack-Signature"
        )
        if not signature:
            raise InvalidSignatureError("x-paystack-signature header missing")

        expected = hmac.new(
            key=self._webhook_secret.encode("utf-8"),
            msg=raw_body,
            digestmod=hashlib.sha512,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise InvalidSignatureError("HMAC-SHA-512 signature mismatch")

        import json as _json

        event_body: dict[str, Any] = _json.loads(raw_body)
        data = event_body.get("data", {})
        return WebhookEvent(
            vendor_reference=data.get("reference", ""),
            status=self._map_status(data.get("status", "pending")),
            amount_minor=int(data.get("amount") or 0),
            currency=data.get("currency", "NGN"),
            fee_minor=int(data.get("fees") or 0),
            raw_event_redacted=_redact(event_body),
            verified_at=_iso_now(),
        )

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _map_status(vendor_status: str) -> PaymentStatus:
        mapping = {
            "success": PaymentStatus.SUCCEEDED,
            "failed": PaymentStatus.FAILED,
            "abandoned": PaymentStatus.FAILED,
            "pending": PaymentStatus.PENDING,
            "reversed": PaymentStatus.REFUNDED,
        }
        return mapping.get(vendor_status, PaymentStatus.PENDING)

    async def _post(self, path: str, *, json: dict[str, Any]) -> dict[str, Any]:
        if self._secret_key is None:
            raise RuntimeError(
                "PaystackAdapter live mode requires ATLAS_PAYSTACK_SECRET_KEY."
            )
        async with httpx.AsyncClient(base_url=PAYSTACK_API_BASE, timeout=_TIMEOUT) as client:
            response = await client.post(
                path,
                json=json,
                headers={"Authorization": f"Bearer {self._secret_key}"},
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
            return payload

    async def _get(self, path: str) -> dict[str, Any]:
        if self._secret_key is None:
            raise RuntimeError(
                "PaystackAdapter live mode requires ATLAS_PAYSTACK_SECRET_KEY."
            )
        async with httpx.AsyncClient(base_url=PAYSTACK_API_BASE, timeout=_TIMEOUT) as client:
            response = await client.get(
                path,
                headers={"Authorization": f"Bearer {self._secret_key}"},
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
            return payload
