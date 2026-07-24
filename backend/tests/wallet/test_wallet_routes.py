"""GET /api/v1/users/me/wallet — balance chip integration tests."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.identity import mailhog_sender
from atlas.wallet import service as wallet_service


@pytest.fixture(autouse=True)
def _stub_mailhog(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[tuple[str, str, str]]]:
    sent: list[tuple[str, str, str]] = []

    async def _stub(*, phone_e164: str, code: str, purpose: str) -> None:
        sent.append((phone_e164, code, purpose))

    monkeypatch.setattr(mailhog_sender, "send_otp", _stub)
    yield sent


async def _register_login(
    client: AsyncClient, sent_stub: list[tuple[str, str, str]]
) -> tuple[uuid.UUID, str]:
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
    return user_id, login.json()["access_token"]


class TestBalanceEndpoint:
    async def test_new_user_returns_zero(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, token = await _register_login(client, _stub_mailhog)
        response = await client.get(
            "/api/v1/users/me/wallet",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body == {
            "balance_minor": 0,
            "currency": "NGN",
            "updated_at": body["updated_at"],  # opaque, just check present + ISO
        }
        # ISO-8601 UTC shape check.
        assert body["updated_at"].endswith("Z") or "+00:00" in body["updated_at"]

    async def test_after_deposit_returns_amount(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        user_id, token = await _register_login(client, _stub_mailhog)
        await wallet_service.record_deposit(
            db_session,
            user_id=user_id,
            amount_minor=250_00,
            external_ref="chip-test",
            idempotency_key=f"chip-{uuid.uuid4()}",
        )
        await db_session.commit()

        response = await client.get(
            "/api/v1/users/me/wallet",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["balance_minor"] == 250_00

    async def test_unauthenticated_returns_401(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/users/me/wallet")
        assert response.status_code == 401
