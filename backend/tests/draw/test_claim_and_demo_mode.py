"""W7 Day 1 tests — winner claim endpoint + demo_mode config effect."""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.audit_log.models import AuditLog
from atlas.draw import crypto as seed_crypto
from atlas.draw.models import Draw, DrawWinner
from atlas.identity import mailhog_sender
from atlas.identity.models import User
from atlas.skill.models import (
    SkillQuestion,
    SkillQuestionOption,
)
from atlas.ticket.models import Ticket


@pytest.fixture(autouse=True)
def _stub_mailhog(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[tuple[str, str, str]]]:
    sent: list[tuple[str, str, str]] = []

    async def _stub(*, phone_e164: str, code: str, purpose: str) -> None:
        sent.append((phone_e164, code, purpose))

    monkeypatch.setattr(mailhog_sender, "send_otp", _stub)
    yield sent


@pytest.fixture(autouse=True)
def _stub_notification(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _stub(**_: object) -> None:
        pass

    monkeypatch.setattr(mailhog_sender, "send_notification", _stub)


async def _seed_draw(session: AsyncSession) -> Draw:
    now = datetime.now(UTC)
    draw_id = uuid.uuid4()
    seed = hashlib.sha256(b"claim-seed-" + draw_id.bytes).digest()
    draw = Draw(
        id=draw_id,
        prize_copy="test prize",
        ticket_price_minor=500_00,
        currency="NGN",
        close_time=now + timedelta(hours=1),
        draw_time=now + timedelta(hours=2),
        state="sales_open",
        commitment=hashlib.sha256(seed + draw_id.bytes).hexdigest(),
        server_seed_encrypted=seed_crypto.encrypt_server_seed(seed),
    )
    session.add(draw)
    q = SkillQuestion(prompt="Q")
    session.add(q)
    await session.flush()
    session.add(
        SkillQuestionOption(
            question_id=q.id, option_text="correct", is_correct=True, display_order=0
        )
    )
    await session.commit()
    return draw


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


async def _make_winner(
    session: AsyncSession, *, draw: Draw
) -> tuple[User, Ticket, DrawWinner]:
    """Insert a user + ticket + winner row directly (skip the paid flow
    for these targeted claim tests)."""
    user = User(
        email=f"w-{uuid.uuid4().hex[:8]}@example.com",
        phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
        date_of_birth=date(1993, 3, 12),
        status="active",
    )
    session.add(user)
    await session.flush()
    ticket = Ticket(
        draw_id=draw.id,
        user_id=user.id,
        ticket_number=1,
        entry_source="paid",
        idempotency_key=f"claim-{uuid.uuid4()}",
    )
    session.add(ticket)
    await session.flush()
    winner = DrawWinner(
        draw_id=draw.id,
        position=0,
        ticket_id=ticket.id,
        user_id=user.id,
        is_primary=True,
    )
    session.add(winner)
    await session.commit()
    return user, ticket, winner


async def _login_as(
    client: AsyncClient, db_session: AsyncSession, user: User
) -> str:
    """Bypass the OTP prerequisite of password_service.set_password by
    writing the password_hash directly, then hitting POST /sessions."""
    import bcrypt

    password = "test-password-123"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user.password_hash = hashed
    await db_session.commit()

    login = await client.post(
        "/api/v1/sessions",
        json={"email": user.email, "password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    return login.json()["access_token"]


class TestClaimHappyPath:
    async def test_winner_claims_prize(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        user, ticket, _ = await _make_winner(db_session, draw=draw)
        token = await _login_as(client, db_session, user)

        response = await client.post(
            f"/api/v1/draws/{draw.id}/winners/{ticket.id}/claim",
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["contact_status"] == "claimed"
        assert body["is_primary"] is True

        # Audit event fired.
        event = (
            await db_session.execute(
                select(AuditLog).where(AuditLog.event_name == "draw.winner_claimed")
            )
        ).scalar_one()
        assert event.payload["ticket_id"] == str(ticket.id)


class TestClaimAuthorization:
    async def test_non_winner_returns_403(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, ticket, _ = await _make_winner(db_session, draw=draw)
        # A totally different user tries to claim.
        _, _, other_token = await _register_login(client, _stub_mailhog)

        response = await client.post(
            f"/api/v1/draws/{draw.id}/winners/{ticket.id}/claim",
            headers={"Authorization": f"Bearer {other_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "winner_forbidden"

    async def test_unknown_winner_returns_404(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, token = await _register_login(client, _stub_mailhog)
        response = await client.post(
            f"/api/v1/draws/{draw.id}/winners/{uuid.uuid4()}/claim",
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 404

    async def test_already_claimed_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        user, ticket, _ = await _make_winner(db_session, draw=draw)
        token = await _login_as(client, db_session, user)

        first = await client.post(
            f"/api/v1/draws/{draw.id}/winners/{ticket.id}/claim",
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert first.status_code == 200

        # Different Idempotency-Key so we exercise the service-level
        # "already claimed" guard.
        second = await client.post(
            f"/api/v1/draws/{draw.id}/winners/{ticket.id}/claim",
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert second.status_code == 409

    async def test_unauthenticated_returns_401(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        draw = await _seed_draw(db_session)
        response = await client.post(
            f"/api/v1/draws/{draw.id}/winners/{uuid.uuid4()}/claim",
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 401


class TestDemoModeConfig:
    """Config-level behaviour of demo_mode (seed script wiring is
    smoke-tested via the seed_v0_5.py subprocess in the Day 5 rehearsal)."""

    def test_prod_safety_rejects_demo_mode_true(self) -> None:
        from pydantic import ValidationError

        from atlas.config import Settings

        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]
                env="production",
                database_url="postgresql+asyncpg://user:pass@host:5432/db",
                jwt_signing_key="a" * 40,
                otp_pepper="b" * 40,
                paystack_webhook_secret="c" * 40,
                wallet_allow_stub_draw=False,
                paystack_stub_mode=False,
                paystack_secret_key="sk_live_key_00000000",
                paystack_public_key="pk_live_key_00000000",
                draw_entropy_mode="live",
                demo_mode=True,  # ← should fail prod safety
            )

    def test_demo_mode_default_false(self) -> None:
        """Baseline safety — default construction (dev env) leaves the
        flag off so nothing turns on the compressed timing by accident."""
        from atlas.config import Settings

        s = Settings(  # type: ignore[call-arg]
            database_url="postgresql+asyncpg://user:pass@host:5432/db",
            jwt_signing_key="a" * 40,
            otp_pepper="b" * 40,
            paystack_webhook_secret="c" * 40,
        )
        assert s.demo_mode is False
