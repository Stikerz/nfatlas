"""POST /api/v1/draws/{id}/reveal — integration tests through the full stack."""

from __future__ import annotations

import hashlib
import hmac
import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.audit_log.models import AuditLog
from atlas.config import get_settings
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


def _sign(body: bytes) -> str:
    secret = get_settings().paystack_webhook_secret.get_secret_value()
    return hmac.new(
        key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha512
    ).hexdigest()


async def _seed_draw(session: AsyncSession, *, state: str = "sales_open") -> Draw:
    now = datetime.now(UTC)
    draw_id = uuid.uuid4()
    seed = hashlib.sha256(b"reveal-seed-" + draw_id.bytes).digest()
    draw = Draw(
        id=draw_id,
        prize_copy="test prize",
        ticket_price_minor=500_00,
        currency="NGN",
        close_time=now + timedelta(hours=1),
        draw_time=now + timedelta(hours=2),
        state=state,
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
    session.add(
        SkillQuestionOption(
            question_id=q.id, option_text="wrong", is_correct=False, display_order=1
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


async def _mint_tickets_direct(
    session: AsyncSession, *, draw: Draw, count: int
) -> list[uuid.UUID]:
    """Insert N tickets via the ORM directly — avoids the full purchase
    flow round-trip in tests that only need the ticket pool populated."""
    ids: list[uuid.UUID] = []
    for i in range(count):
        user = User(
            email=f"u-{uuid.uuid4().hex[:8]}@example.com",
            phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
            date_of_birth=date(1993, 3, 12),
            status="active",
        )
        session.add(user)
        await session.flush()
        ticket = Ticket(
            draw_id=draw.id,
            user_id=user.id,
            ticket_number=i + 1,
            entry_source="paid",
            idempotency_key=f"reveal-test-{uuid.uuid4()}",
        )
        session.add(ticket)
        await session.flush()
        ids.append(ticket.id)
    await session.commit()
    return ids


async def _admin_close(
    client: AsyncClient, draw_id: uuid.UUID, admin_token: str
) -> None:
    response = await client.post(
        f"/api/v1/draws/{draw_id}/close",
        headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 200


class TestRevealHappyPath:
    async def test_reveal_flips_state_and_writes_6_winners(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        await _mint_tickets_direct(db_session, draw=draw, count=10)

        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await _admin_close(client, draw.id, admin_token)

        response = await client.post(
            f"/api/v1/draws/{draw.id}/reveal",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["state"] == "revealed"
        assert body["winner_count"] == 6
        assert body["revealed_at"] is not None

        # Winners table populated in order.
        winners = (
            await db_session.execute(
                select(DrawWinner)
                .where(DrawWinner.draw_id == draw.id)
                .order_by(DrawWinner.position)
            )
        ).scalars().all()
        assert [w.position for w in winners] == list(range(6))
        assert winners[0].is_primary is True
        assert all(w.is_primary is False for w in winners[1:])

        # Reveal_inputs blob populated.
        await db_session.refresh(draw)
        assert draw.reveal_inputs["mode"] == "stub"
        assert len(draw.reveal_inputs["bitcoin_hash"]) == 64

    async def test_reveal_audit_chain(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        await _mint_tickets_direct(db_session, draw=draw, count=6)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await _admin_close(client, draw.id, admin_token)
        await client.post(
            f"/api/v1/draws/{draw.id}/reveal",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )

        events = (
            await db_session.execute(
                select(AuditLog.event_name).order_by(AuditLog.seq)
            )
        ).scalars().all()
        # One draw.revealed summary + one draw.winner_selected per winner (6).
        assert events.count("draw.revealed") == 1
        assert events.count("draw.winner_selected") == 6

        # user_id_hash present, raw user_id NOT.
        winner_events = (
            await db_session.execute(
                select(AuditLog).where(AuditLog.event_name == "draw.winner_selected")
            )
        ).scalars().all()
        for event in winner_events:
            assert "user_id_hash" in event.payload
            assert "user_id" not in event.payload


class TestRevealIdempotency:
    async def test_double_reveal_is_noop(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        await _mint_tickets_direct(db_session, draw=draw, count=6)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await _admin_close(client, draw.id, admin_token)

        first = await client.post(
            f"/api/v1/draws/{draw.id}/reveal",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        # Different Idempotency-Key exercises the service-level no-op guard.
        second = await client.post(
            f"/api/v1/draws/{draw.id}/reveal",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert first.status_code == 200
        assert second.status_code == 200

        winner_count = (
            await db_session.execute(
                select(func.count()).select_from(DrawWinner).where(
                    DrawWinner.draw_id == draw.id
                )
            )
        ).scalar_one()
        assert winner_count == 6


class TestRevealStateGuards:
    async def test_reveal_on_sales_open_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session, state="sales_open")
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        response = await client.post(
            f"/api/v1/draws/{draw.id}/reveal",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "draw_state_error"

    async def test_reveal_with_no_tickets_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        """Draw closed with 0 tickets → 409 not_enough_tickets. A demo-
        time misconfiguration surfaces as a client error, not 500,
        because the operator can still fix it (add tickets or void
        the draw)."""
        draw = await _seed_draw(db_session)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await _admin_close(client, draw.id, admin_token)
        response = await client.post(
            f"/api/v1/draws/{draw.id}/reveal",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "not_enough_tickets"


class TestRevealAuth:
    async def test_non_admin_returns_403(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, user_token = await _register_login(client, _stub_mailhog)
        response = await client.post(
            f"/api/v1/draws/{draw.id}/reveal",
            headers={"Authorization": f"Bearer {user_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 403


class TestWinnersEndpoint:
    async def test_returns_winners_in_position_order(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        await _mint_tickets_direct(db_session, draw=draw, count=6)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await _admin_close(client, draw.id, admin_token)
        await client.post(
            f"/api/v1/draws/{draw.id}/reveal",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )

        response = await client.get(
            f"/api/v1/draws/{draw.id}/winners",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 6
        assert [i["position"] for i in items] == list(range(6))
        assert items[0]["is_primary"] is True

    async def test_pre_reveal_returns_empty_list(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, user_token = await _register_login(client, _stub_mailhog)
        response = await client.get(
            f"/api/v1/draws/{draw.id}/winners",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        assert response.json() == {"items": []}

    async def test_unknown_draw_returns_404(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, user_token = await _register_login(client, _stub_mailhog)
        response = await client.get(
            f"/api/v1/draws/{uuid.uuid4()}/winners",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
