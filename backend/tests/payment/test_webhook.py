"""POST /api/v1/payments/webhooks/paystack — integration tests.

Signed against the real HMAC-SHA-512 path using the same webhook secret
the app reads from config, so the verifier is exercised end-to-end.
Each test posts a valid intent first (via the identity + payment
routes) then delivers a signed webhook against that intent's
vendor_reference.
"""

from __future__ import annotations

import hashlib
import hmac
import itertools
import json
import uuid
from collections.abc import Iterator
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog
from atlas.config import get_settings
from atlas.identity import mailhog_sender
from atlas.payment.models import PaymentIntentRow
from atlas.payment.providers import paystack_fixtures
from atlas.payment.providers.protocol import PaymentStatus
from atlas.wallet import queries as wallet_queries
from atlas.wallet import service as wallet_service
from atlas.wallet.models import LedgerAccount, LedgerEntry


@pytest.fixture(autouse=True)
def _stub_mailhog(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[tuple[str, str, str]]]:
    sent: list[tuple[str, str, str]] = []

    async def _stub(*, phone_e164: str, code: str, purpose: str) -> None:
        sent.append((phone_e164, code, purpose))

    monkeypatch.setattr(mailhog_sender, "send_otp", _stub)
    yield sent


def _sign(body: bytes) -> str:
    secret = get_settings().paystack_webhook_secret.get_secret_value()
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha512,
    ).hexdigest()


async def _register_login_and_create_intent(
    client: AsyncClient,
    sent_stub: list[tuple[str, str, str]],
    *,
    amount_minor: int = 500_00,
) -> tuple[uuid.UUID, str, str]:
    """Full auth + intent flow. Returns (user_id, vendor_reference, email)."""
    email = f"kemi-{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+2348030{uuid.uuid4().int % 1_000_000:06d}"

    r = await client.post(
        "/api/v1/users",
        json={
            "email": email,
            "phone_e164": phone,
            "date_of_birth": date(1993, 3, 12).isoformat(),
            "terms_accepted": True,
        },
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    user_id = uuid.UUID(r.json()["user_id"])

    await client.post(
        "/api/v1/otps",
        json={"user_id": str(user_id), "purpose": "registration"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    code = sent_stub[-1][1]
    await client.post(
        "/api/v1/otps/verify",
        json={"user_id": str(user_id), "purpose": "registration", "code": code},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    password = "correct horse battery staple"
    await client.post(
        f"/api/v1/users/{user_id}/password",
        json={"password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    login = await client.post(
        "/api/v1/sessions",
        json={"email": email, "password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    token = login.json()["access_token"]

    intent_response = await client.post(
        "/api/v1/payments/intents",
        json={"amount_minor": amount_minor, "method": "card"},
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    return user_id, intent_response.json()["vendor_reference"], email


class TestChargeSuccess:
    async def test_valid_signature_credits_wallet_and_posts_fee(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        user_id, vendor_ref, email = await _register_login_and_create_intent(
            client, _stub_mailhog, amount_minor=500_00
        )
        body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference=vendor_ref, amount_minor=500_00, email=email
            )
        ).encode("utf-8")

        response = await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=body,
            headers={
                "x-paystack-signature": _sign(body),
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200

        intent = (
            await db_session.execute(
                select(PaymentIntentRow).where(
                    PaymentIntentRow.vendor_reference == vendor_ref
                )
            )
        ).scalar_one()
        assert intent.status == PaymentStatus.SUCCEEDED.value

        # user_wallet should hold the full gross deposit.
        user_wallet = await wallet_service.get_or_create_user_wallet(
            db_session, user_id=user_id
        )
        assert await wallet_queries.balance_of(db_session, account_id=user_wallet.id) == 500_00

        # Fee is a separate ledger transaction — expect the operator-revenue
        # and clearing balances to reflect only the fee side after both
        # transactions land.
        expected_fee = paystack_fixtures.compute_fee_kobo(500_00)
        clearing = (
            await db_session.execute(
                select(LedgerAccount).where(
                    LedgerAccount.account_type == "payment_gateway_clearing"
                )
            )
        ).scalar_one()
        # clearing: +500_00 (from deposit) minus fee (from fee tx) = net debit balance.
        # balance_of returns SUM(direction*amount) treating C as positive, D as
        # negative — clearing normal debit balance is negative under that
        # convention.
        clearing_balance = await wallet_queries.balance_of(
            db_session, account_id=clearing.id
        )
        assert clearing_balance == -(500_00 - expected_fee)

    async def test_replay_is_no_op(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, vendor_ref, email = await _register_login_and_create_intent(
            client, _stub_mailhog, amount_minor=500_00
        )
        body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference=vendor_ref, amount_minor=500_00, email=email
            )
        ).encode("utf-8")
        sig = _sign(body)

        first = await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=body,
            headers={"x-paystack-signature": sig, "Content-Type": "application/json"},
        )
        second = await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=body,
            headers={"x-paystack-signature": sig, "Content-Type": "application/json"},
        )

        assert first.status_code == 200
        assert second.status_code == 200

        # Ledger sanity: exactly two transactions (deposit + fee) — one
        # transaction_id per pair, so 4 rows total, 2 distinct tx ids.
        row_count = (
            await db_session.execute(select(func.count()).select_from(LedgerEntry))
        ).scalar_one()
        assert row_count == 4

        # One payment.confirmed audit event (not two).
        confirmed_count = (
            await db_session.execute(
                select(func.count()).select_from(AuditLog).where(
                    AuditLog.event_name == "payment.confirmed"
                )
            )
        ).scalar_one()
        assert confirmed_count == 1

    async def test_audit_chain_covers_the_full_flow(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, vendor_ref, email = await _register_login_and_create_intent(
            client, _stub_mailhog, amount_minor=500_00
        )
        body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference=vendor_ref, amount_minor=500_00, email=email
            )
        ).encode("utf-8")
        await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=body,
            headers={"x-paystack-signature": _sign(body), "Content-Type": "application/json"},
        )

        rows = (
            await db_session.execute(select(AuditLog).order_by(AuditLog.seq))
        ).scalars().all()
        events = [r.event_name for r in rows]
        # Wallet events fire from inside apply_succeeded before the summary
        # payment.confirmed event; that ordering is deliberate so the
        # ledger side-effects are chained before the "we processed this
        # webhook" marker.
        assert events == [
            "user.registered",
            "otp.issued",
            "otp.verified",
            "user.password_set",
            "session.created",
            "payment.intent_created",
            "wallet.deposit_credited",
            "wallet.payment_fee_posted",
            "payment.confirmed",
        ]
        # Chain integrity end-to-end.
        for prev, curr in itertools.pairwise(rows):
            assert curr.prev_hash == prev.row_hash


class TestChargeFailed:
    async def test_charge_failed_marks_intent_no_ledger(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, vendor_ref, email = await _register_login_and_create_intent(
            client, _stub_mailhog, amount_minor=500_00
        )
        body = json.dumps(
            paystack_fixtures.charge_failed_event(
                reference=vendor_ref, amount_minor=500_00, email=email
            )
        ).encode("utf-8")

        response = await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=body,
            headers={"x-paystack-signature": _sign(body), "Content-Type": "application/json"},
        )

        assert response.status_code == 200

        intent = (
            await db_session.execute(
                select(PaymentIntentRow).where(
                    PaymentIntentRow.vendor_reference == vendor_ref
                )
            )
        ).scalar_one()
        assert intent.status == PaymentStatus.FAILED.value

        row_count = (
            await db_session.execute(select(func.count()).select_from(LedgerEntry))
        ).scalar_one()
        assert row_count == 0

        events = (
            await db_session.execute(
                select(AuditLog.event_name).order_by(AuditLog.seq)
            )
        ).scalars().all()
        assert events[-1] == "payment.failed"


class TestSignatureFailures:
    async def test_bad_signature_returns_401_no_state_change(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, vendor_ref, email = await _register_login_and_create_intent(
            client, _stub_mailhog, amount_minor=500_00
        )
        body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference=vendor_ref, amount_minor=500_00, email=email
            )
        ).encode("utf-8")

        response = await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=body,
            headers={"x-paystack-signature": "0" * 128, "Content-Type": "application/json"},
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "invalid_signature"

        intent = (
            await db_session.execute(
                select(PaymentIntentRow).where(
                    PaymentIntentRow.vendor_reference == vendor_ref
                )
            )
        ).scalar_one()
        assert intent.status == "initiated"
        row_count = (
            await db_session.execute(select(func.count()).select_from(LedgerEntry))
        ).scalar_one()
        assert row_count == 0

    async def test_missing_signature_returns_401(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=b'{"event":"charge.success","data":{}}',
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "invalid_signature"


class TestUnknownRefsAndEvents:
    async def test_unknown_vendor_reference_returns_200_no_state(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference="atlas-does-not-exist",
                amount_minor=500_00,
                email="ghost@example.com",
            )
        ).encode("utf-8")

        response = await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=body,
            headers={"x-paystack-signature": _sign(body), "Content-Type": "application/json"},
        )

        assert response.status_code == 200
        row_count = (
            await db_session.execute(select(func.count()).select_from(LedgerEntry))
        ).scalar_one()
        assert row_count == 0

    async def test_zero_fee_skips_fee_transaction(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        user_id, vendor_ref, email = await _register_login_and_create_intent(
            client, _stub_mailhog, amount_minor=500_00
        )
        # Hand-craft an event whose fees are 0 (edge case: promo / free tx).
        event_body = paystack_fixtures.charge_success_event(
            reference=vendor_ref, amount_minor=500_00, email=email
        )
        event_body["data"]["fees"] = 0
        body = json.dumps(event_body).encode("utf-8")

        await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=body,
            headers={"x-paystack-signature": _sign(body), "Content-Type": "application/json"},
        )

        # Only the deposit transaction (2 entries) — no fee side.
        row_count = (
            await db_session.execute(select(func.count()).select_from(LedgerEntry))
        ).scalar_one()
        assert row_count == 2

        user_wallet = await wallet_service.get_or_create_user_wallet(
            db_session, user_id=user_id
        )
        assert await wallet_queries.balance_of(db_session, account_id=user_wallet.id) == 500_00
