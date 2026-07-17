"""POST /api/v1/payments/intents — integration tests against real Postgres.

Auth flow (register → verify OTP → set password → login) is reused from
the identity module so the endpoint test exercises a realistic caller.
The Paystack adapter runs in its default stub mode; the tests assert on
the mock checkout URL shape.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog
from atlas.identity import mailhog_sender
from atlas.payment.models import PaymentIntentRow


@pytest.fixture(autouse=True)
def _stub_mailhog(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[tuple[str, str, str]]]:
    sent: list[tuple[str, str, str]] = []

    async def _stub(*, phone_e164: str, code: str, purpose: str) -> None:
        sent.append((phone_e164, code, purpose))

    monkeypatch.setattr(mailhog_sender, "send_otp", _stub)
    yield sent


async def _register_and_login(
    client: AsyncClient,
    sent_stub: list[tuple[str, str, str]],
) -> tuple[uuid.UUID, str, str]:
    """Returns (user_id, email, bearer_token). Mirrors the identity Day 5 flow."""
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
    assert r.status_code == 201, r.text
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
    assert login.status_code == 201, login.text
    return user_id, email, login.json()["access_token"]


class TestCreateIntentHappyPath:
    async def test_returns_201_with_mock_checkout_url(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        user_id, _, token = await _register_and_login(client, _stub_mailhog)

        response = await client.post(
            "/api/v1/payments/intents",
            json={"amount_minor": 500_00, "method": "card", "description": "Top-up"},
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert uuid.UUID(body["payment_intent_id"])
        assert body["vendor_reference"].startswith("atlas-")
        assert body["checkout_url"].startswith("http://mock-paystack.local/checkout/")
        assert body["amount_minor"] == 500_00
        assert body["currency"] == "NGN"
        assert body["status"] == "initiated"
        assert body["expires_at"] is not None

        row = (
            await db_session.execute(select(PaymentIntentRow).where(PaymentIntentRow.user_id == user_id))
        ).scalar_one()
        assert row.vendor_reference == body["vendor_reference"]
        assert row.checkout_url == body["checkout_url"]
        assert row.raw_response["data"]["reference"] == body["vendor_reference"]

    async def test_writes_payment_intent_created_audit_event(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, token = await _register_and_login(client, _stub_mailhog)

        await client.post(
            "/api/v1/payments/intents",
            json={"amount_minor": 500_00, "method": "card"},
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )

        events = (
            await db_session.execute(
                select(AuditLog.event_name).order_by(AuditLog.seq)
            )
        ).scalars().all()
        assert "payment.intent_created" in events
        assert events[-1] == "payment.intent_created"


class TestIdempotency:
    async def test_same_key_same_body_returns_cached_response(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _user_id, _email, token = await _register_and_login(client, _stub_mailhog)
        key = str(uuid.uuid4())
        body = {"amount_minor": 500_00, "method": "card", "description": "Top-up"}

        first = await client.post(
            "/api/v1/payments/intents",
            json=body,
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": key},
        )
        second = await client.post(
            "/api/v1/payments/intents",
            json=body,
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": key},
        )

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json() == second.json()

        rows = (await db_session.execute(select(PaymentIntentRow))).scalars().all()
        assert len(rows) == 1

    async def test_same_key_different_body_returns_409(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, token = await _register_and_login(client, _stub_mailhog)
        key = str(uuid.uuid4())

        await client.post(
            "/api/v1/payments/intents",
            json={"amount_minor": 500_00, "method": "card"},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": key},
        )
        conflict = await client.post(
            "/api/v1/payments/intents",
            json={"amount_minor": 1_000_00, "method": "card"},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": key},
        )

        assert conflict.status_code == 409
        assert conflict.json()["detail"]["code"] == "idempotency_key_conflict"

    async def test_missing_idempotency_key_returns_400(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, token = await _register_and_login(client, _stub_mailhog)

        response = await client.post(
            "/api/v1/payments/intents",
            json={"amount_minor": 500_00, "method": "card"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "idempotency_key_required"


class TestAuth:
    async def test_unauthenticated_returns_401(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/payments/intents",
            json={"amount_minor": 500_00, "method": "card"},
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 401


class TestValidation:
    async def test_zero_amount_rejected(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, token = await _register_and_login(client, _stub_mailhog)
        response = await client.post(
            "/api/v1/payments/intents",
            json={"amount_minor": 0, "method": "card"},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 422

    async def test_unknown_method_rejected(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, token = await _register_and_login(client, _stub_mailhog)
        response = await client.post(
            "/api/v1/payments/intents",
            json={"amount_minor": 500_00, "method": "cheque"},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 422
