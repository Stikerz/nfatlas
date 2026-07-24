"""POST /api/v1/tickets/free — admin transcribes a free-route entry."""

from __future__ import annotations

import hashlib
import hmac
import json
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
from atlas.draw.models import Draw
from atlas.identity import mailhog_sender
from atlas.payment.providers import paystack_fixtures
from atlas.skill.models import (
    SkillQuestion,
    SkillQuestionOption,
)
from atlas.ticket.models import FreeEntrySlip, Ticket


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
    seed = b"test-seed-" + draw_id.bytes
    draw = Draw(
        id=draw_id,
        prize_copy="test prize",
        ticket_price_minor=500_00,
        currency="NGN",
        close_time=now + timedelta(days=1),
        draw_time=now + timedelta(days=1, hours=1),
        state=state,
        commitment=hashlib.sha256(seed + draw_id.bytes).hexdigest(),
        server_seed_encrypted=seed.hex(),
    )
    session.add(draw)
    q = SkillQuestion(prompt="Q1")
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
        assert db_session is not None, "make_admin requires db_session"
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


class TestFreeEntryHappyPath:
    async def test_admin_transcribes_free_ticket(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        subject_id, _, _ = await _register_login(client, _stub_mailhog)

        response = await client.post(
            "/api/v1/tickets/free",
            json={
                "draw_id": str(draw.id),
                "subject_user_id": str(subject_id),
                "slip_reference": "FE-2026-07-30-0001",
            },
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["subject_user_id"] == str(subject_id)
        assert body["entry_source"] == "free"
        assert body["ticket_number"] == 1

        # Slip row exists.
        slip = (
            await db_session.execute(
                select(FreeEntrySlip).where(
                    FreeEntrySlip.slip_reference == "FE-2026-07-30-0001"
                )
            )
        ).scalar_one()
        assert slip.draw_id == draw.id
        assert slip.subject_user_id == subject_id

        # Audit event uses slip_reference_hash, not the raw reference.
        event = (
            await db_session.execute(
                select(AuditLog).where(AuditLog.event_name == "ticket.free_transcribed")
            )
        ).scalar_one()
        expected_hash = hashlib.sha256(b"FE-2026-07-30-0001").hexdigest()
        assert event.payload["slip_reference_hash"] == expected_hash
        assert "slip_reference" not in event.payload

    async def test_free_ticket_appears_in_subject_users_list(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        subject_id, _, subject_token = await _register_login(client, _stub_mailhog)

        await client.post(
            "/api/v1/tickets/free",
            json={
                "draw_id": str(draw.id),
                "subject_user_id": str(subject_id),
                "slip_reference": "FE-2026-07-30-XYZ",
            },
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        response = await client.get(
            "/api/v1/tickets/me",
            headers={"Authorization": f"Bearer {subject_token}"},
        )
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["entry_source"] == "free"


class TestAuthorization:
    async def test_non_admin_returns_403(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        # Both are regular users — no superadmin grant.
        _, _, user_token = await _register_login(client, _stub_mailhog)
        subject_id, _, _ = await _register_login(client, _stub_mailhog)

        response = await client.post(
            "/api/v1/tickets/free",
            json={
                "draw_id": str(draw.id),
                "subject_user_id": str(subject_id),
                "slip_reference": "FE-should-fail",
            },
            headers={"Authorization": f"Bearer {user_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "operator_role_required"

        # No slip written, no ticket minted.
        slip_count = (
            await db_session.execute(select(func.count()).select_from(FreeEntrySlip))
        ).scalar_one()
        assert slip_count == 0

    async def test_unauthenticated_returns_401(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        draw = await _seed_draw(db_session)
        response = await client.post(
            "/api/v1/tickets/free",
            json={
                "draw_id": str(draw.id),
                "subject_user_id": str(uuid.uuid4()),
                "slip_reference": "FE-no-auth",
            },
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 401


class TestSlipUniqueness:
    async def test_duplicate_slip_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        subject_a, _, _ = await _register_login(client, _stub_mailhog)
        subject_b, _, _ = await _register_login(client, _stub_mailhog)

        first = await client.post(
            "/api/v1/tickets/free",
            json={
                "draw_id": str(draw.id),
                "subject_user_id": str(subject_a),
                "slip_reference": "FE-DUP-01",
            },
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert first.status_code == 201

        second = await client.post(
            "/api/v1/tickets/free",
            json={
                "draw_id": str(draw.id),
                "subject_user_id": str(subject_b),
                "slip_reference": "FE-DUP-01",
            },
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert second.status_code == 409
        assert second.json()["detail"]["code"] == "slip_already_transcribed"


class TestSubjectValidation:
    async def test_unknown_subject_user_returns_404(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        response = await client.post(
            "/api/v1/tickets/free",
            json={
                "draw_id": str(draw.id),
                "subject_user_id": str(uuid.uuid4()),
                "slip_reference": "FE-unknown-user",
            },
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "user_not_found"

    async def test_closed_draw_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session, state="sales_closed")
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        subject_id, _, _ = await _register_login(client, _stub_mailhog)

        response = await client.post(
            "/api/v1/tickets/free",
            json={
                "draw_id": str(draw.id),
                "subject_user_id": str(subject_id),
                "slip_reference": "FE-closed",
            },
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "draw_not_open"


class TestMixedNumbering:
    async def test_paid_then_free_gets_1_then_2(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        """Free-entry parity by construction: ticket_numbers are drawn
        from the same monotonic per-draw sequence. Paid ticket #1,
        free ticket #2."""
        draw = await _seed_draw(db_session)

        # Paid ticket first.
        _, email, token = await _register_login(client, _stub_mailhog)
        next_resp = await client.get(
            f"/api/v1/draws/{draw.id}/skill-questions/next",
            headers={"Authorization": f"Bearer {token}"},
        )
        q = next_resp.json()
        correct_id = next(o["id"] for o in q["options"] if o["text"] == "correct")
        await client.post(
            f"/api/v1/skill-questions/attempts/{q['attempt_id']}/answer",
            json={"option_id": correct_id},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        purchase = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": q["attempt_id"]},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        vendor_ref = purchase.json()["vendor_reference"]
        body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference=vendor_ref, amount_minor=draw.ticket_price_minor, email=email
            )
        ).encode("utf-8")
        await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=body,
            headers={"x-paystack-signature": _sign(body), "Content-Type": "application/json"},
        )

        # Then free ticket.
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        subject_id, _, _ = await _register_login(client, _stub_mailhog)
        await client.post(
            "/api/v1/tickets/free",
            json={
                "draw_id": str(draw.id),
                "subject_user_id": str(subject_id),
                "slip_reference": "FE-parity-01",
            },
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )

        rows = (
            await db_session.execute(
                select(Ticket).where(Ticket.draw_id == draw.id).order_by(Ticket.ticket_number)
            )
        ).scalars().all()
        assert [(t.entry_source, t.ticket_number) for t in rows] == [
            ("paid", 1),
            ("free", 2),
        ]
