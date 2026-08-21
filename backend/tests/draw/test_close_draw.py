"""POST /api/v1/draws/{id}/close — integration tests."""

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
from atlas.draw import crypto as seed_crypto
from atlas.draw.models import Draw
from atlas.identity import mailhog_sender
from atlas.payment.providers import paystack_fixtures
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
    seed = hashlib.sha256(b"test-seed-" + draw_id.bytes).digest()
    draw = Draw(
        id=draw_id,
        prize_copy="test prize",
        ticket_price_minor=500_00,
        currency="NGN",
        close_time=now + timedelta(days=1),
        draw_time=now + timedelta(days=1, hours=1),
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


async def _buy_paid_ticket(
    client: AsyncClient, draw_id: uuid.UUID, token: str, email: str
) -> str:
    """Full purchase → webhook path. Returns vendor_reference for the intent."""
    next_resp = await client.get(
        f"/api/v1/draws/{draw_id}/skill-questions/next",
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
        json={"draw_id": str(draw_id), "entitlement_id": q["attempt_id"]},
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    vendor_ref = purchase.json()["vendor_reference"]
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
    return vendor_ref


class TestCloseHappyPath:
    async def test_close_flips_state_and_computes_hash(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, email, token = await _register_login(client, _stub_mailhog)
        await _buy_paid_ticket(client, draw.id, token, email)

        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        response = await client.post(
            f"/api/v1/draws/{draw.id}/close",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["state"] == "sales_closed"
        assert len(body["tickets_hash"]) == 64  # sha256 hex

        # Audit event carries ticket count + hash.
        event = (
            await db_session.execute(
                select(AuditLog).where(AuditLog.event_name == "draw.entries_snapshot")
            )
        ).scalar_one()
        assert event.payload["ticket_count"] == 1
        assert event.payload["tickets_hash"] == body["tickets_hash"]

    async def test_close_with_no_tickets_produces_empty_list_hash(
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
            f"/api/v1/draws/{draw.id}/close",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 200
        # SHA-256 of JCS-canonical of empty list is a known constant.
        import rfc8785
        expected = hashlib.sha256(rfc8785.dumps([])).hexdigest()
        assert response.json()["tickets_hash"] == expected

    async def test_tickets_hash_deterministic_across_runs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        """Insert two tickets by hand with specific IDs; close; hash must
        match SHA-256 of the JCS-canonical ordered list — no dependency
        on wall-clock or PRNG."""
        import rfc8785

        from atlas.identity.models import User

        draw = await _seed_draw(db_session)
        user = User(
            email=f"u-{uuid.uuid4().hex[:8]}@example.com",
            phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
            date_of_birth=date(1993, 3, 12),
            status="active",
        )
        db_session.add(user)
        await db_session.flush()

        t1_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
        t2_id = uuid.UUID("22222222-2222-2222-2222-222222222222")
        db_session.add(
            Ticket(
                id=t1_id,
                draw_id=draw.id,
                user_id=user.id,
                ticket_number=1,
                entry_source="paid",
                idempotency_key=f"det-1-{uuid.uuid4()}",
            )
        )
        db_session.add(
            Ticket(
                id=t2_id,
                draw_id=draw.id,
                user_id=user.id,
                ticket_number=2,
                entry_source="free",
                idempotency_key=f"det-2-{uuid.uuid4()}",
            )
        )
        await db_session.commit()

        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        response = await client.post(
            f"/api/v1/draws/{draw.id}/close",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        expected = hashlib.sha256(
            rfc8785.dumps([str(t1_id), str(t2_id)])
        ).hexdigest()
        assert response.json()["tickets_hash"] == expected


class TestCloseIdempotency:
    async def test_double_close_is_noop(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        # First close.
        await client.post(
            f"/api/v1/draws/{draw.id}/close",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        # Second close with a DIFFERENT idempotency key exercises the
        # service-level idempotency (state==sales_closed → no-op).
        response = await client.post(
            f"/api/v1/draws/{draw.id}/close",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 200
        # Only one entries_snapshot event.
        count = (
            await db_session.execute(
                select(func.count()).select_from(AuditLog).where(
                    AuditLog.event_name == "draw.entries_snapshot"
                )
            )
        ).scalar_one()
        assert count == 1


class TestCloseStateGuards:
    async def test_close_on_revealed_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session, state="revealed")
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        response = await client.post(
            f"/api/v1/draws/{draw.id}/close",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "draw_state_error"

    async def test_purchase_against_closed_draw_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        """W5 ticket.service.is_sales_open guard — regression check that
        it holds after W6's close_draw flips state."""
        draw = await _seed_draw(db_session)
        _, _, user_token = await _register_login(client, _stub_mailhog)

        # Get entitlement BEFORE close (skill next requires sales_open too).
        next_resp = await client.get(
            f"/api/v1/draws/{draw.id}/skill-questions/next",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        q = next_resp.json()
        correct_id = next(o["id"] for o in q["options"] if o["text"] == "correct")
        await client.post(
            f"/api/v1/skill-questions/attempts/{q['attempt_id']}/answer",
            json={"option_id": correct_id},
            headers={"Authorization": f"Bearer {user_token}", "Idempotency-Key": str(uuid.uuid4())},
        )

        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await client.post(
            f"/api/v1/draws/{draw.id}/close",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )

        purchase = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": q["attempt_id"]},
            headers={"Authorization": f"Bearer {user_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert purchase.status_code == 409
        assert purchase.json()["detail"]["code"] == "draw_not_open"


class TestCloseAuth:
    async def test_non_admin_returns_403(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, user_token = await _register_login(client, _stub_mailhog)
        response = await client.post(
            f"/api/v1/draws/{draw.id}/close",
            headers={"Authorization": f"Bearer {user_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 403

    async def test_unknown_draw_returns_404(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        response = await client.post(
            f"/api/v1/draws/{uuid.uuid4()}/close",
            headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 404
