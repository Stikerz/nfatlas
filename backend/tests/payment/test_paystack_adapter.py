"""Paystack adapter unit tests.

Covers three surfaces:
  - stub mode returns the deterministic fixture shape (no HTTP fired)
  - live mode POSTs to https://api.paystack.co with the bearer key and
    the reference derived from idempotency_key
  - verify_webhook exercises the real HMAC-SHA-512 path — a body signed
    with the configured webhook secret round-trips through the
    verifier without error; a mismatched signature raises.

Live-mode HTTP is mocked with `pytest-httpx`; no real network calls.
The webhook secret matches the CI env var so signing helpers here can
generate a valid `x-paystack-signature` header locally.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid

import pytest

from atlas.config import get_settings
from atlas.payment.providers import paystack_fixtures
from atlas.payment.providers.paystack import PaystackAdapter, _reference_for
from atlas.payment.providers.protocol import (
    InvalidSignatureError,
    PaymentIntent,
    PaymentMethod,
    PaymentStatus,
)


def _make_intent(*, idempotency_key: str | None = None) -> PaymentIntent:
    return PaymentIntent(
        user_id=str(uuid.uuid4()),
        amount_minor=500_00,
        currency="NGN",
        idempotency_key=idempotency_key or f"deposit-{uuid.uuid4()}",
        method=PaymentMethod.CARD,
        description="Ticket top-up",
        email="kemi@example.com",
    )


class TestReferenceDerivation:
    def test_reference_is_deterministic(self) -> None:
        key = "the-same-key"
        assert _reference_for(key) == _reference_for(key)

    def test_reference_prefix(self) -> None:
        ref = _reference_for("k1")
        assert ref.startswith("atlas-")


class TestStubMode:
    async def test_create_intent_returns_fixture_shape(self) -> None:
        adapter = PaystackAdapter(stub_mode=True)
        intent = _make_intent()

        result = await adapter.create_intent(intent)

        assert result.status is PaymentStatus.INITIATED
        assert result.vendor_reference == _reference_for(intent.idempotency_key)
        assert result.checkout_url is not None
        assert result.checkout_url.startswith("http://mock-paystack.local/checkout/")
        assert result.inline_token is not None
        assert result.fee_minor == 0
        # redaction of a payload without sensitive fields is a no-op — the
        # fixture doesn't carry an authorization block, so the raw_response
        # round-trips intact.
        assert result.raw_response_redacted["data"]["reference"] == result.vendor_reference

    async def test_create_intent_replay_returns_same_reference(self) -> None:
        adapter = PaystackAdapter(stub_mode=True)
        key = f"deposit-{uuid.uuid4()}"

        first = await adapter.create_intent(_make_intent(idempotency_key=key))
        second = await adapter.create_intent(_make_intent(idempotency_key=key))

        assert first.vendor_reference == second.vendor_reference
        assert first.checkout_url == second.checkout_url


class TestLiveMode:
    """`pytest-httpx` mocks the wire — no real Paystack call goes out."""

    async def test_create_intent_posts_to_paystack_with_bearer(
        self,
        httpx_mock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # A live-mode adapter needs the secret key present. We wire it in
        # via a fresh Settings instance instead of touching os.environ so
        # ADR-012's env-var discipline stays intact.
        from pydantic import SecretStr

        settings = get_settings()
        live_settings = settings.model_copy(
            update={
                "paystack_stub_mode": False,
                "paystack_secret_key": SecretStr("sk_test_live_mode_key_for_test_only"),
            }
        )
        monkeypatch.setattr("atlas.config.get_settings", lambda: live_settings)
        monkeypatch.setattr(
            "atlas.payment.providers.paystack.get_settings",
            lambda: live_settings,
        )

        intent = _make_intent()
        reference = _reference_for(intent.idempotency_key)
        response_body = paystack_fixtures.initialize_response(
            reference=reference,
            amount_minor=intent.amount_minor,
            email=intent.email,
        )
        httpx_mock.add_response(
            method="POST",
            url="https://api.paystack.co/transaction/initialize",
            json=response_body,
        )

        adapter = PaystackAdapter()  # picks up live_settings via monkeypatch
        result = await adapter.create_intent(intent)

        assert result.vendor_reference == reference
        # Inspect the request that went out.
        (request,) = httpx_mock.get_requests()
        assert request.headers["Authorization"] == "Bearer sk_test_live_mode_key_for_test_only"
        sent = json.loads(request.content)
        assert sent["email"] == intent.email
        assert sent["amount"] == intent.amount_minor
        assert sent["reference"] == reference

    async def test_create_intent_live_mode_missing_secret_raises(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        settings = get_settings()
        live_settings = settings.model_copy(
            update={"paystack_stub_mode": False, "paystack_secret_key": None},
        )
        monkeypatch.setattr(
            "atlas.payment.providers.paystack.get_settings",
            lambda: live_settings,
        )
        adapter = PaystackAdapter()

        with pytest.raises(RuntimeError, match="requires ATLAS_PAYSTACK_SECRET_KEY"):
            await adapter.create_intent(_make_intent())


class TestVerifyWebhook:
    """HMAC-SHA-512 path — exercised in both stub and live modes."""

    def _sign(self, body: bytes) -> str:
        secret = get_settings().paystack_webhook_secret.get_secret_value()
        return hmac.new(
            key=secret.encode("utf-8"),
            msg=body,
            digestmod=hashlib.sha512,
        ).hexdigest()

    def test_valid_signature_returns_webhook_event(self) -> None:
        body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference="atlas-abc123",
                amount_minor=500_00,
                email="kemi@example.com",
            )
        ).encode("utf-8")

        adapter = PaystackAdapter(stub_mode=True)
        event = adapter.verify_webhook(
            body,
            {"x-paystack-signature": self._sign(body)},
        )

        assert event.vendor_reference == "atlas-abc123"
        assert event.status is PaymentStatus.SUCCEEDED
        assert event.amount_minor == 500_00
        assert event.fee_minor == paystack_fixtures.compute_fee_kobo(500_00)
        assert event.raw_event_redacted["event"] == "charge.success"

    def test_bad_signature_raises(self) -> None:
        body = b'{"event":"charge.success","data":{}}'
        adapter = PaystackAdapter(stub_mode=True)
        with pytest.raises(InvalidSignatureError):
            adapter.verify_webhook(
                body,
                {"x-paystack-signature": "0" * 128},
            )

    def test_missing_signature_header_raises(self) -> None:
        adapter = PaystackAdapter(stub_mode=True)
        with pytest.raises(InvalidSignatureError):
            adapter.verify_webhook(b"{}", {})

    def test_case_insensitive_signature_header(self) -> None:
        body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference="atlas-xyz", amount_minor=1_000_00, email="a@b.c"
            )
        ).encode("utf-8")
        adapter = PaystackAdapter(stub_mode=True)
        event = adapter.verify_webhook(
            body,
            {"X-Paystack-Signature": self._sign(body)},
        )
        assert event.status is PaymentStatus.SUCCEEDED

    def test_charge_failed_event_maps_to_failed(self) -> None:
        body = json.dumps(
            paystack_fixtures.charge_failed_event(
                reference="atlas-fail", amount_minor=200_00, email="a@b.c"
            )
        ).encode("utf-8")
        adapter = PaystackAdapter(stub_mode=True)
        event = adapter.verify_webhook(
            body,
            {"x-paystack-signature": self._sign(body)},
        )
        assert event.status is PaymentStatus.FAILED
        assert event.fee_minor == 0


class TestRedaction:
    def test_authorization_code_is_stripped(self) -> None:
        from atlas.payment.providers.paystack import _redact

        payload = {
            "data": {
                "reference": "atlas-abc",
                "authorization": {
                    "authorization_code": "AUTH_secret_do_not_leak",
                    "bin": "408408",
                    "last4": "4081",
                    "channel": "card",
                    "bank": "Test Bank",
                },
            }
        }
        redacted = _redact(payload)
        auth = redacted["data"]["authorization"]
        assert "authorization_code" not in auth
        assert "bin" not in auth
        assert "last4" not in auth
        assert auth["channel"] == "card"
        assert auth["bank"] == "Test Bank"


class TestFeeSchedule:
    """Golden vectors for the stub fee computation."""

    @pytest.mark.parametrize(
        ("gross_minor", "expected_fee_minor"),
        [
            (500_00, 100_00),        # ₦500     → ₦100 flat
            (2_500_00, 100_00),      # ₦2,500   → ₦100 flat (threshold inclusive)
            (10_000_00, 25_000),     # ₦10,000  → ₦150 (1.5%) + ₦100 = ₦250 → 25_000 kobo
            (200_000_00, 200_000),   # ₦200,000 → capped at ₦2,000 = 200_000 kobo
        ],
    )
    def test_fee_kobo(self, gross_minor: int, expected_fee_minor: int) -> None:
        assert paystack_fixtures.compute_fee_kobo(gross_minor) == expected_fee_minor
