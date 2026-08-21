"""Winner-notification consumer — reads WINNER_SELECTED_V1 payload → mailhog."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import date

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog
from atlas.identity import mailhog_sender
from atlas.identity.models import User
from atlas.notification import winner as winner_notification


async def _make_user(db_session: AsyncSession, *, email: str) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
        date_of_birth=date(1993, 3, 12),
        status="active",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
def _stub_mailhog_sender(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[list[dict[str, str]]]:
    calls: list[dict[str, str]] = []

    async def _stub(*, to_email: str, subject: str, body: str) -> None:
        calls.append({"to_email": to_email, "subject": subject, "body": body})

    monkeypatch.setattr(mailhog_sender, "send_notification", _stub)
    yield calls


class TestDeliverFromPayload:
    async def test_primary_winner_gets_you_won_email(
        self,
        db_session: AsyncSession,
        _stub_mailhog_sender: list[dict[str, str]],
    ) -> None:
        user = await _make_user(db_session, email="winner@example.com")
        payload = {
            "draw_id": str(uuid.uuid4()),
            "winner_id": str(uuid.uuid4()),
            "ticket_id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "position": 0,
            "is_primary": True,
            "prize_copy": "Win a car",
        }

        await winner_notification.deliver_from_payload(db_session, payload)

        assert len(_stub_mailhog_sender) == 1
        call = _stub_mailhog_sender[0]
        assert call["to_email"] == "winner@example.com"
        assert call["subject"] == "You won a draw"
        assert "Win a car" in call["body"]
        assert "primary" in call["body"]

    async def test_reserve_winner_gets_reserve_email(
        self,
        db_session: AsyncSession,
        _stub_mailhog_sender: list[dict[str, str]],
    ) -> None:
        user = await _make_user(db_session, email="reserve@example.com")
        payload = {
            "draw_id": str(uuid.uuid4()),
            "winner_id": str(uuid.uuid4()),
            "ticket_id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "position": 3,
            "is_primary": False,
            "prize_copy": "Win a car",
        }

        await winner_notification.deliver_from_payload(db_session, payload)

        assert len(_stub_mailhog_sender) == 1
        assert _stub_mailhog_sender[0]["subject"] == "You're a reserve winner"
        assert "reserve #3" in _stub_mailhog_sender[0]["body"]

    async def test_audit_event_fires_before_delivery(
        self,
        db_session: AsyncSession,
        _stub_mailhog_sender: list[dict[str, str]],
    ) -> None:
        user = await _make_user(db_session, email="audit@example.com")
        payload = {
            "draw_id": str(uuid.uuid4()),
            "winner_id": str(uuid.uuid4()),
            "ticket_id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "position": 0,
            "is_primary": True,
            "prize_copy": "Win a car",
        }

        await winner_notification.deliver_from_payload(db_session, payload)

        count = (
            await db_session.execute(
                select(func.count()).select_from(AuditLog).where(
                    AuditLog.event_name == "notification.winner_selected"
                )
            )
        ).scalar_one()
        assert count == 1

    async def test_audit_fires_even_when_smtp_raises(
        self,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        user = await _make_user(db_session, email="fail@example.com")

        async def _boom(**_: object) -> None:
            raise RuntimeError("mailhog down")

        monkeypatch.setattr(mailhog_sender, "send_notification", _boom)

        payload = {
            "draw_id": str(uuid.uuid4()),
            "winner_id": str(uuid.uuid4()),
            "ticket_id": str(uuid.uuid4()),
            "user_id": str(user.id),
            "position": 0,
            "is_primary": True,
            "prize_copy": "Win a car",
        }

        with pytest.raises(RuntimeError, match="mailhog down"):
            await winner_notification.deliver_from_payload(db_session, payload)

        # Audit still landed BEFORE the SMTP call raised.
        count = (
            await db_session.execute(
                select(func.count()).select_from(AuditLog).where(
                    AuditLog.event_name == "notification.winner_selected"
                )
            )
        ).scalar_one()
        assert count == 1
