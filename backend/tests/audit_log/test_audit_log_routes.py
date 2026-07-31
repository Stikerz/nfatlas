"""GET /api/v1/audit-log — admin read endpoint tests."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.identity import mailhog_sender


@pytest.fixture(autouse=True)
def _stub_mailhog(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[tuple[str, str, str]]]:
    sent: list[tuple[str, str, str]] = []

    async def _stub(*, phone_e164: str, code: str, purpose: str) -> None:
        sent.append((phone_e164, code, purpose))

    monkeypatch.setattr(mailhog_sender, "send_otp", _stub)
    yield sent


async def _register_login(
    client: AsyncClient,
    sent_stub: list[tuple[str, str, str]],
    db_session: AsyncSession | None = None,
    make_admin: bool = False,
) -> tuple[uuid.UUID, str, str]:
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
    if make_admin:
        assert db_session is not None
        await admin_service.grant_role(
            db_session, user_id=user_id, role_code=admin_service.SUPERADMIN_ROLE
        )
        await db_session.commit()
    login = await client.post(
        "/api/v1/sessions",
        json={"email": email, "password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    return user_id, email, login.json()["access_token"]


class TestAuditLogEndpoint:
    async def test_admin_reads_page_with_chain_verified(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        # Register a couple of users to generate audit events.
        await _register_login(client, _stub_mailhog)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )

        response = await client.get(
            "/api/v1/audit-log?limit=10",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["chain_verified"] is True
        assert body["chain_verify_reason"] is None
        assert len(body["items"]) > 0
        # Newest-first ordering.
        seqs = [item["seq"] for item in body["items"]]
        assert seqs == sorted(seqs, reverse=True)

    async def test_event_name_filter(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        await _register_login(client, _stub_mailhog)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        response = await client.get(
            "/api/v1/audit-log?event_name=user.registered",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        for item in response.json()["items"]:
            assert item["event_name"] == "user.registered"

    async def test_non_admin_returns_403(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, token = await _register_login(client, _stub_mailhog)
        response = await client.get(
            "/api/v1/audit-log",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "operator_role_required"

    async def test_unauthenticated_returns_401(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/audit-log")
        assert response.status_code == 401

    async def test_pagination_via_before_seq(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        # Generate enough events to page through.
        for _ in range(3):
            await _register_login(client, _stub_mailhog)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )

        first = await client.get(
            "/api/v1/audit-log?limit=3",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert first.status_code == 200
        first_page = first.json()
        assert len(first_page["items"]) == 3
        assert first_page["next_before_seq"] is not None

        second = await client.get(
            f"/api/v1/audit-log?limit=3&before_seq={first_page['next_before_seq']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert second.status_code == 200
        second_page = second.json()
        # Second page rows are strictly older (smaller seq) than the first.
        first_min_seq = min(item["seq"] for item in first_page["items"])
        for item in second_page["items"]:
            assert item["seq"] < first_min_seq

    async def test_limit_upper_bound_500(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        response = await client.get(
            "/api/v1/audit-log?limit=501",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # FastAPI Query validator rejects > 500.
        assert response.status_code == 422
