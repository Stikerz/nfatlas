"""RBAC service + session-current enrichment tests."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.admin.models import Permission, Role
from atlas.identity import mailhog_sender
from atlas.identity.models import User


@pytest.fixture(autouse=True)
def _stub_mailhog(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _stub(*, phone_e164: str, code: str, purpose: str) -> None:
        return None

    monkeypatch.setattr(mailhog_sender, "send_otp", _stub)


async def _make_user(client: AsyncClient, *, email: str, phone: str, password: str) -> tuple[str, str]:
    reg = await client.post(
        "/api/v1/users",
        json={
            "email": email,
            "phone_e164": phone,
            "date_of_birth": date(1993, 3, 12).isoformat(),
            "terms_accepted": True,
        },
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert reg.status_code == 201, reg.text
    user_id = reg.json()["user_id"]

    # Server-issue an OTP and read it back from the DB for the test.
    await client.post(
        "/api/v1/otps",
        json={"user_id": user_id, "purpose": "registration"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )

    return user_id, email


async def test_seed_migration_lands_two_roles(db_session: AsyncSession) -> None:
    codes = (await db_session.execute(select(Role.code))).scalars().all()
    assert set(codes) == {"superadmin", "user"}

    # Permissions table exists but is empty in V0.5.
    perms = (await db_session.execute(select(Permission.code))).scalars().all()
    assert list(perms) == []


async def test_grant_role_is_idempotent(db_session: AsyncSession) -> None:
    user = User(
        email=f"tester-{uuid.uuid4().hex[:8]}@example.com",
        phone_e164="+2348039999998",
        date_of_birth=date(1993, 3, 12),
        status="active",
    )
    db_session.add(user)
    await db_session.flush()

    await admin_service.grant_role(db_session, user_id=user.id, role_code="superadmin")
    await admin_service.grant_role(db_session, user_id=user.id, role_code="superadmin")
    roles = await admin_service.roles_for(db_session, user_id=user.id)
    assert roles == ["superadmin"]


async def test_roles_for_returns_sorted_union(db_session: AsyncSession) -> None:
    user = User(
        email=f"multi-{uuid.uuid4().hex[:8]}@example.com",
        phone_e164="+2348039999997",
        date_of_birth=date(1993, 3, 12),
        status="active",
    )
    db_session.add(user)
    await db_session.flush()

    await admin_service.grant_role(db_session, user_id=user.id, role_code="user")
    await admin_service.grant_role(db_session, user_id=user.id, role_code="superadmin")

    assert await admin_service.roles_for(db_session, user_id=user.id) == [
        "superadmin",
        "user",
    ]
    assert await admin_service.is_superadmin(db_session, user_id=user.id)


async def test_sessions_current_returns_roles(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    # Register + fully activate a user, log in, then grant superadmin.
    email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    phone = "+2348030000099"
    password = "correct horse battery staple"

    reg = await client.post(
        "/api/v1/users",
        json={
            "email": email,
            "phone_e164": phone,
            "date_of_birth": date(1993, 3, 12).isoformat(),
            "terms_accepted": True,
        },
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    user_id_str = reg.json()["user_id"]
    user_uuid = uuid.UUID(user_id_str)

    from atlas.identity import otp_service

    # Bypass the mailhog path — issue + verify via the service directly.
    _otp, code = await otp_service.issue(db_session, user_id=user_uuid, purpose="registration")
    await db_session.commit()
    await otp_service.verify(
        db_session, user_id=user_uuid, purpose="registration", code=code
    )
    await db_session.commit()

    await client.post(
        f"/api/v1/users/{user_id_str}/password",
        json={"password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    login = await client.post(
        "/api/v1/sessions",
        json={"email": email, "password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    token = login.json()["access_token"]

    # Without any role: is_admin=False, roles empty.
    current = await client.get(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = current.json()
    assert body["email"] == email
    assert body["roles"] == []
    assert body["is_admin"] is False

    # Grant superadmin, re-read.
    await admin_service.grant_role(db_session, user_id=user_uuid, role_code="superadmin")
    await db_session.commit()

    current2 = await client.get(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    body2 = current2.json()
    assert body2["roles"] == ["superadmin"]
    assert body2["is_admin"] is True
