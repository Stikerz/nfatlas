"""POST /api/v1/tickets/purchase + charge.success webhook → ticket minted.

Covers the full ticket-purpose payment flow end-to-end plus the
ticket_number monotonicity contract.
"""

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

from atlas.audit_log.models import AuditLog
from atlas.config import get_settings
from atlas.draw.models import Draw
from atlas.identity import mailhog_sender
from atlas.payment.providers import paystack_fixtures
from atlas.skill.models import (
    SkillQuestion,
    SkillQuestionAttempt,
    SkillQuestionOption,
)
from atlas.ticket.models import Ticket
from atlas.wallet import queries as wallet_queries
from atlas.wallet import service as wallet_service
from atlas.wallet.models import LedgerAccount, LedgerEntry


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


async def _seed_draw(session: AsyncSession, *, ticket_price: int = 500_00) -> Draw:
    now = datetime.now(UTC)
    draw_id = uuid.uuid4()
    seed = b"test-seed-" + draw_id.bytes
    draw = Draw(
        id=draw_id,
        prize_copy="test prize",
        ticket_price_minor=ticket_price,
        currency="NGN",
        close_time=now + timedelta(days=1),
        draw_time=now + timedelta(days=1, hours=1),
        state="sales_open",
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
    client: AsyncClient, sent_stub: list[tuple[str, str, str]]
) -> tuple[uuid.UUID, str, str]:
    """Returns (user_id, email, bearer_token)."""
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
    return user_id, email, login.json()["access_token"]


async def _pass_skill_check(
    client: AsyncClient, draw_id: uuid.UUID, token: str
) -> uuid.UUID:
    """Answer correctly and return the entitlement id (= attempt_id)."""
    next_resp = await client.get(
        f"/api/v1/draws/{draw_id}/skill-questions/next",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = next_resp.json()
    correct_id = next(o["id"] for o in body["options"] if o["text"] == "correct")
    answer = await client.post(
        f"/api/v1/skill-questions/attempts/{body['attempt_id']}/answer",
        json={"option_id": correct_id},
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert answer.status_code == 200, answer.text
    return uuid.UUID(body["attempt_id"])


class TestPurchaseHappyPath:
    async def test_returns_checkout_url_but_no_ticket_yet(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        user_id, _, token = await _register_login(client, _stub_mailhog)
        entitlement = await _pass_skill_check(client, draw.id, token)

        response = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": str(entitlement)},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert uuid.UUID(body["payment_intent_id"])
        assert body["vendor_reference"].startswith("atlas-")
        assert body["checkout_url"].startswith("http://mock-paystack.local/checkout/")
        assert body["amount_minor"] == draw.ticket_price_minor

        # No ticket exists yet — mint waits for the webhook.
        ticket_count = (
            await db_session.execute(
                select(func.count()).select_from(Ticket).where(Ticket.user_id == user_id)
            )
        ).scalar_one()
        assert ticket_count == 0

    async def test_webhook_mints_ticket_and_posts_revenue_not_wallet(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        user_id, email, token = await _register_login(client, _stub_mailhog)
        entitlement = await _pass_skill_check(client, draw.id, token)

        purchase = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": str(entitlement)},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        vendor_ref = purchase.json()["vendor_reference"]

        webhook_body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference=vendor_ref, amount_minor=draw.ticket_price_minor, email=email
            )
        ).encode("utf-8")
        webhook_response = await client.post(
            "/api/v1/payments/webhooks/paystack",
            content=webhook_body,
            headers={"x-paystack-signature": _sign(webhook_body), "Content-Type": "application/json"},
        )
        assert webhook_response.status_code == 200

        # Ticket exists, entry_source='paid'.
        ticket = (
            await db_session.execute(
                select(Ticket).where(Ticket.user_id == user_id)
            )
        ).scalar_one()
        assert ticket.entry_source == "paid"
        assert ticket.draw_id == draw.id
        assert ticket.ticket_number == 1

        # user_wallet stays at zero (direct-to-Paystack ticket path).
        user_wallet = await wallet_service.get_or_create_user_wallet(
            db_session, user_id=user_id
        )
        assert await wallet_queries.balance_of(db_session, account_id=user_wallet.id) == 0

        # operator_revenue was credited (gross minus fee net).
        operator_revenue = (
            await db_session.execute(
                select(LedgerAccount).where(
                    LedgerAccount.account_type == "operator_revenue"
                )
            )
        ).scalar_one()
        expected_fee = paystack_fixtures.compute_fee_kobo(draw.ticket_price_minor)
        # +gross (sale credit) minus fee (fee debit) → net credit balance.
        assert await wallet_queries.balance_of(
            db_session, account_id=operator_revenue.id
        ) == draw.ticket_price_minor - expected_fee

    async def test_entitlement_marked_consumed_after_webhook(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, email, token = await _register_login(client, _stub_mailhog)
        entitlement = await _pass_skill_check(client, draw.id, token)

        purchase = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": str(entitlement)},
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

        attempt = await db_session.get(SkillQuestionAttempt, entitlement)
        assert attempt is not None
        assert attempt.consumed_at is not None

    async def test_webhook_replay_no_duplicate_ticket(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        user_id, email, token = await _register_login(client, _stub_mailhog)
        entitlement = await _pass_skill_check(client, draw.id, token)

        purchase = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": str(entitlement)},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        vendor_ref = purchase.json()["vendor_reference"]
        body = json.dumps(
            paystack_fixtures.charge_success_event(
                reference=vendor_ref, amount_minor=draw.ticket_price_minor, email=email
            )
        ).encode("utf-8")
        sig = _sign(body)

        for _ in range(2):
            await client.post(
                "/api/v1/payments/webhooks/paystack",
                content=body,
                headers={"x-paystack-signature": sig, "Content-Type": "application/json"},
            )

        ticket_count = (
            await db_session.execute(
                select(func.count()).select_from(Ticket).where(Ticket.user_id == user_id)
            )
        ).scalar_one()
        assert ticket_count == 1

        # Only one ticket-sale ledger tx even after replay.
        ledger_count = (
            await db_session.execute(select(func.count()).select_from(LedgerEntry))
        ).scalar_one()
        # 2 entries per sale tx + 2 entries per fee tx = 4.
        assert ledger_count == 4


class TestEntitlementValidation:
    async def test_unknown_entitlement_returns_404(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, token = await _register_login(client, _stub_mailhog)
        response = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "entitlement_not_found"

    async def test_cross_user_entitlement_returns_403(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, _, token_a = await _register_login(client, _stub_mailhog)
        entitlement = await _pass_skill_check(client, draw.id, token_a)
        _, _, token_b = await _register_login(client, _stub_mailhog)

        response = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": str(entitlement)},
            headers={"Authorization": f"Bearer {token_b}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "entitlement_forbidden"

    async def test_wrong_answer_entitlement_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        """Answer wrong → attempt has no entitlement_expires_at → attempt to
        redeem it should fail with entitlement_not_correct."""
        draw = await _seed_draw(db_session)
        _, _, token = await _register_login(client, _stub_mailhog)
        # Answer wrong.
        next_resp = await client.get(
            f"/api/v1/draws/{draw.id}/skill-questions/next",
            headers={"Authorization": f"Bearer {token}"},
        )
        body = next_resp.json()
        wrong_id = next(o["id"] for o in body["options"] if o["text"] != "correct")
        await client.post(
            f"/api/v1/skill-questions/attempts/{body['attempt_id']}/answer",
            json={"option_id": wrong_id},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )

        response = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": body["attempt_id"]},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "entitlement_not_correct"

    async def test_draw_not_open_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        from sqlalchemy import update

        draw = await _seed_draw(db_session)
        _, _, token = await _register_login(client, _stub_mailhog)
        entitlement = await _pass_skill_check(client, draw.id, token)

        # Close the draw between skill-check and purchase.
        await db_session.execute(
            update(Draw).where(Draw.id == draw.id).values(state="sales_closed")
        )
        await db_session.commit()

        response = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": str(entitlement)},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "draw_not_open"


class TestTicketNumberMonotonicity:
    async def test_three_purchases_get_1_2_3(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        vendor_refs: list[str] = []
        emails: list[str] = []
        for _ in range(3):
            _, email, token = await _register_login(client, _stub_mailhog)
            entitlement = await _pass_skill_check(client, draw.id, token)
            purchase = await client.post(
                "/api/v1/tickets/purchase",
                json={"draw_id": str(draw.id), "entitlement_id": str(entitlement)},
                headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
            )
            vendor_refs.append(purchase.json()["vendor_reference"])
            emails.append(email)

        for ref, email in zip(vendor_refs, emails, strict=True):
            body = json.dumps(
                paystack_fixtures.charge_success_event(
                    reference=ref, amount_minor=draw.ticket_price_minor, email=email
                )
            ).encode("utf-8")
            await client.post(
                "/api/v1/payments/webhooks/paystack",
                content=body,
                headers={"x-paystack-signature": _sign(body), "Content-Type": "application/json"},
            )

        numbers = (
            await db_session.execute(
                select(Ticket.ticket_number).where(Ticket.draw_id == draw.id).order_by(Ticket.ticket_number)
            )
        ).scalars().all()
        assert list(numbers) == [1, 2, 3]


class TestGetMyTickets:
    async def test_returns_only_own_tickets(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, email_a, token_a = await _register_login(client, _stub_mailhog)
        _, email_b, token_b = await _register_login(client, _stub_mailhog)

        for token, email in ((token_a, email_a), (token_b, email_b)):
            entitlement = await _pass_skill_check(client, draw.id, token)
            purchase = await client.post(
                "/api/v1/tickets/purchase",
                json={"draw_id": str(draw.id), "entitlement_id": str(entitlement)},
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

        resp_a = await client.get(
            "/api/v1/tickets/me",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert len(resp_a.json()["items"]) == 1

    async def test_unauthenticated_returns_401(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/tickets/me")
        assert response.status_code == 401


class TestAuditChain:
    async def test_ticket_flow_writes_expected_events(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        _, email, token = await _register_login(client, _stub_mailhog)
        entitlement = await _pass_skill_check(client, draw.id, token)
        purchase = await client.post(
            "/api/v1/tickets/purchase",
            json={"draw_id": str(draw.id), "entitlement_id": str(entitlement)},
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

        events = (
            await db_session.execute(
                select(AuditLog.event_name).order_by(AuditLog.seq)
            )
        ).scalars().all()
        # Post-webhook chain includes the ticket-sale ledger event and
        # the ticket.issued event, then fee, then payment.confirmed.
        for expected in (
            "skill_question.issued",
            "skill_question.answered_correct",
            "payment.intent_created",
            "wallet.ticket_sale_recorded",
            "ticket.issued",
            "ticket.paid_purchase_completed",
            "wallet.payment_fee_posted",
            "payment.confirmed",
        ):
            assert expected in events, f"missing event: {expected} (got {events})"
