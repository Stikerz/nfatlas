"""OTP + password + session — integration tests against real Postgres.

Covers Day 3 scope per week-3-build-plan §2 Day 3 and §5 (integration list).
Mailhog delivery is patched to a no-op — the real SMTP path is smoke-tested
manually via docker compose.
"""

from __future__ import annotations

import itertools
import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog
from atlas.identity import mailhog_sender
from atlas.identity.models import OTP, User


@pytest.fixture(autouse=True)
def _stub_mailhog(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[tuple[str, str, str]]]:
    """No-op mailhog sender; records dispatched (phone, code, purpose) tuples."""
    sent: list[tuple[str, str, str]] = []

    async def _stub(*, phone_e164: str, code: str, purpose: str) -> None:
        sent.append((phone_e164, code, purpose))

    monkeypatch.setattr(mailhog_sender, "send_otp", _stub)
    yield sent


async def _register(client: AsyncClient) -> tuple[uuid.UUID, str, str]:
    email = f"kemi-{uuid.uuid4().hex[:8]}@example.com"
    phone = "+2348030000001"
    response = await client.post(
        "/api/v1/users",
        json={
            "email": email,
            "phone_e164": phone,
            "date_of_birth": date(1993, 3, 12).isoformat(),
            "terms_accepted": True,
        },
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 201, response.text
    return uuid.UUID(response.json()["user_id"]), email, phone


async def _issue(
    client: AsyncClient, user_id: uuid.UUID, purpose: str = "registration"
) -> uuid.UUID:
    response = await client.post(
        "/api/v1/otps",
        json={"user_id": str(user_id), "purpose": purpose},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 201, response.text
    return uuid.UUID(response.json()["otp_id"])


async def _issue_and_get_code(
    client: AsyncClient,
    user_id: uuid.UUID,
    sent_stub: list[tuple[str, str, str]],
    purpose: str = "registration",
) -> str:
    before = len(sent_stub)
    await _issue(client, user_id, purpose=purpose)
    assert len(sent_stub) == before + 1
    return sent_stub[-1][1]


async def test_otp_happy_path_writes_two_audit_events(
    client: AsyncClient,
    db_session: AsyncSession,
    _stub_mailhog: list[tuple[str, str, str]],
) -> None:
    user_id, _, phone = await _register(client)
    code = await _issue_and_get_code(client, user_id, _stub_mailhog)

    response = await client.post(
        "/api/v1/otps/verify",
        json={"user_id": str(user_id), "purpose": "registration", "code": code},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 200
    assert response.json() == {"verified": True}

    events = (
        await db_session.execute(select(AuditLog.event_name).order_by(AuditLog.seq))
    ).scalars().all()
    assert events == ["user.registered", "otp.issued", "otp.verified"]

    assert _stub_mailhog[0][0] == phone


async def test_otp_wrong_code_writes_verification_failed(
    client: AsyncClient,
    db_session: AsyncSession,
    _stub_mailhog: list[tuple[str, str, str]],
) -> None:
    user_id, _, _ = await _register(client)
    await _issue_and_get_code(client, user_id, _stub_mailhog)

    for _ in range(5):
        response = await client.post(
            "/api/v1/otps/verify",
            json={"user_id": str(user_id), "purpose": "registration", "code": "000000"},
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 400
        assert response.json()["detail"]["reason"] == "wrong_code"

    failed = (
        await db_session.execute(
            select(func.count()).select_from(AuditLog).where(
                AuditLog.event_name == "otp.verification_failed"
            )
        )
    ).scalar_one()
    assert failed == 5


async def test_otp_expired_returns_400(
    client: AsyncClient,
    db_session: AsyncSession,
    _stub_mailhog: list[tuple[str, str, str]],
) -> None:
    user_id, _, _ = await _register(client)
    code = await _issue_and_get_code(client, user_id, _stub_mailhog)

    # Fast-forward the OTP's expiry into the past.
    await db_session.execute(
        update(OTP)
        .where(OTP.user_id == user_id)
        .values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
    )
    await db_session.commit()

    response = await client.post(
        "/api/v1/otps/verify",
        json={"user_id": str(user_id), "purpose": "registration", "code": code},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["reason"] == "expired"


async def test_otp_resend_before_60s_rate_limited(
    client: AsyncClient,
    _stub_mailhog: list[tuple[str, str, str]],
) -> None:
    user_id, _, _ = await _register(client)
    await _issue(client, user_id)

    response = await client.post(
        "/api/v1/otps",
        json={"user_id": str(user_id), "purpose": "registration"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 429
    assert response.json()["detail"]["code"] == "otp_resend_too_soon"


async def test_password_set_without_otp_verify_forbidden(
    client: AsyncClient,
) -> None:
    user_id, _, _ = await _register(client)
    response = await client.post(
        f"/api/v1/users/{user_id}/password",
        json={"password": "not-guessable-9x"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "otp_prerequisite_missing"


async def test_full_register_verify_password_login_flow(
    client: AsyncClient,
    db_session: AsyncSession,
    _stub_mailhog: list[tuple[str, str, str]],
) -> None:
    user_id, email, _ = await _register(client)
    code = await _issue_and_get_code(client, user_id, _stub_mailhog)

    await client.post(
        "/api/v1/otps/verify",
        json={"user_id": str(user_id), "purpose": "registration", "code": code},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )

    password = "correct horse battery staple"
    pw_response = await client.post(
        f"/api/v1/users/{user_id}/password",
        json={"password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert pw_response.status_code == 204

    user = (await db_session.execute(select(User).where(User.id == user_id))).scalar_one()
    await db_session.refresh(user)
    assert user.status == "active"
    assert user.password_hash is not None

    login = await client.post(
        "/api/v1/sessions",
        json={"email": email, "password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert login.status_code == 201
    body = login.json()
    assert body["token_type"] == "Bearer"
    assert body["user_id"] == str(user_id)
    token = body["access_token"]

    current = await client.get(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert current.status_code == 200
    assert current.json()["user_id"] == str(user_id)

    logout = await client.post(
        "/api/v1/sessions/current/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout.status_code == 204

    reused = await client.get(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert reused.status_code == 401
    assert reused.json()["detail"]["code"] == "session_revoked"

    events = (
        await db_session.execute(select(AuditLog.event_name).order_by(AuditLog.seq))
    ).scalars().all()
    assert events == [
        "user.registered",
        "otp.issued",
        "otp.verified",
        "user.password_set",
        "session.created",
        "session.revoked",
    ]

    audit = (await db_session.execute(select(AuditLog).order_by(AuditLog.seq))).scalars().all()
    for prev, curr in itertools.pairwise(audit):
        assert curr.prev_hash == prev.row_hash


async def test_login_wrong_password_returns_401(
    client: AsyncClient,
    _stub_mailhog: list[tuple[str, str, str]],
) -> None:
    user_id, email, _ = await _register(client)
    code = await _issue_and_get_code(client, user_id, _stub_mailhog)
    await client.post(
        "/api/v1/otps/verify",
        json={"user_id": str(user_id), "purpose": "registration", "code": code},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    await client.post(
        f"/api/v1/users/{user_id}/password",
        json={"password": "correct-password-1234"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )

    login = await client.post(
        "/api/v1/sessions",
        json={"email": email, "password": "wrong-password-9999"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert login.status_code == 401
    assert login.json()["detail"]["code"] == "invalid_credentials"


async def test_login_before_password_set_returns_401(
    client: AsyncClient,
) -> None:
    _user_id, email, _ = await _register(client)
    login = await client.post(
        "/api/v1/sessions",
        json={"email": email, "password": "anything-at-all"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert login.status_code == 401


async def test_current_session_without_bearer_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/sessions/current")
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "session_invalid"


async def test_current_session_with_malformed_bearer_returns_401(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/sessions/current",
        headers={"Authorization": "Bearer not.a.jwt"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "session_invalid"
