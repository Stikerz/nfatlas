"""Week 5 exit-gate E2E — the flagship consumer + operator flows end-to-end.

Walks the demo-plan §2 flagship flow steps 1-5, 10:

  Consumer:
    1. register + OTP + password + login
    2. browse the active draw (GET /draws + /draws/{id})
    (3. free-entry disclosure — UI concern, out of scope for backend E2E)
    4. buy paid ticket: skill question → answer correctly → purchase →
       signed webhook → ticket appears
    5. view ticket (GET /tickets/me)

  Operator:
    10. transcribe free-entry slip → subject user's ticket list shows it

Then the assertions the plan §8 exit gate mentions:
  - wallet balance stays at 0 across a paid-ticket purchase (direct-to-
    Paystack; user_wallet is for winnings only in V0.5)
  - full audit chain intact from register → deposit-side revenue post →
    ticket issued → free ticket issued, with prev_hash linkage
"""

from __future__ import annotations

import hashlib
import hmac
import itertools
import json
import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
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


async def _seed_draw_and_pool(session: AsyncSession) -> Draw:
    """Mirror the seed-script shape at demo-time — one sales_open draw
    with a small skill pool. Test scope is per-test truncation so we
    don't rely on the shipped seed script here."""
    now = datetime.now(UTC)
    draw_id = uuid.uuid4()
    seed = hashlib.sha256(b"e2e-seed-" + draw_id.bytes).digest()
    draw = Draw(
        id=draw_id,
        prize_copy="Win ₦2M cash or a Lagos apartment.",
        ticket_price_minor=500_00,
        currency="NGN",
        close_time=now + timedelta(days=3),
        draw_time=now + timedelta(days=3, hours=1),
        state="sales_open",
        commitment=hashlib.sha256(seed + draw_id.bytes).hexdigest(),
        server_seed_encrypted=seed_crypto.encrypt_server_seed(seed),
    )
    session.add(draw)
    # Three questions gives the rotation somewhere to pick from.
    for i in range(3):
        q = SkillQuestion(prompt=f"Question {i}")
        session.add(q)
        await session.flush()
        session.add(
            SkillQuestionOption(
                question_id=q.id, option_text="correct", is_correct=True, display_order=0
            )
        )
        session.add(
            SkillQuestionOption(
                question_id=q.id, option_text="wrong-a", is_correct=False, display_order=1
            )
        )
        session.add(
            SkillQuestionOption(
                question_id=q.id, option_text="wrong-b", is_correct=False, display_order=2
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
    """Full identity flow. Returns (user_id, email, bearer_token)."""
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
    assert r.status_code == 201, r.text
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


async def test_flagship_flow_end_to_end(
    client: AsyncClient,
    db_session: AsyncSession,
    _stub_mailhog: list[tuple[str, str, str]],
) -> None:
    """One test to catch a Week 5 regression regardless of which slice
    broke. If per-slice tests are green and this one fails, look at the
    cross-module wiring: routes registration, migration ordering, seed
    truncation."""
    draw = await _seed_draw_and_pool(db_session)

    # ── step 1: register + login ─────────────────────────────────────────
    _, email, token = await _register_login(client, _stub_mailhog)

    # ── step 2: browse the active draw ───────────────────────────────────
    draws_resp = await client.get("/api/v1/draws")
    assert draws_resp.status_code == 200
    assert str(draw.id) in [d["id"] for d in draws_resp.json()["items"]]

    detail_resp = await client.get(f"/api/v1/draws/{draw.id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["commitment"] == draw.commitment

    # ── wallet chip starts at zero ───────────────────────────────────────
    wallet_resp = await client.get(
        "/api/v1/users/me/wallet",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert wallet_resp.status_code == 200
    assert wallet_resp.json()["balance_minor"] == 0

    # ── step 4a: skill question → correct answer → entitlement ──────────
    next_resp = await client.get(
        f"/api/v1/draws/{draw.id}/skill-questions/next",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert next_resp.status_code == 200
    question = next_resp.json()
    correct_id = next(o["id"] for o in question["options"] if o["text"] == "correct")
    answer_resp = await client.post(
        f"/api/v1/skill-questions/attempts/{question['attempt_id']}/answer",
        json={"option_id": correct_id},
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert answer_resp.status_code == 200
    assert answer_resp.json()["is_correct"] is True

    # ── step 4b: purchase intent ─────────────────────────────────────────
    purchase_resp = await client.post(
        "/api/v1/tickets/purchase",
        json={"draw_id": str(draw.id), "entitlement_id": question["attempt_id"]},
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert purchase_resp.status_code == 201, purchase_resp.text
    purchase = purchase_resp.json()
    assert purchase["checkout_url"].startswith("http://mock-paystack.local/checkout/")
    vendor_ref = purchase["vendor_reference"]

    # ── step 4c: signed webhook → ticket minted ─────────────────────────
    webhook_body = json.dumps(
        paystack_fixtures.charge_success_event(
            reference=vendor_ref, amount_minor=draw.ticket_price_minor, email=email
        )
    ).encode("utf-8")
    wh_resp = await client.post(
        "/api/v1/payments/webhooks/paystack",
        content=webhook_body,
        headers={
            "x-paystack-signature": _sign(webhook_body),
            "Content-Type": "application/json",
        },
    )
    assert wh_resp.status_code == 200

    # ── step 5: view tickets ─────────────────────────────────────────────
    my_tickets = await client.get(
        "/api/v1/tickets/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert my_tickets.status_code == 200
    items = my_tickets.json()["items"]
    assert len(items) == 1
    assert items[0]["entry_source"] == "paid"
    assert items[0]["ticket_number"] == 1

    # Wallet chip: still zero — direct-to-Paystack path never touches it.
    wallet_after = await client.get(
        "/api/v1/users/me/wallet",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert wallet_after.json()["balance_minor"] == 0

    # ── step 10: operator transcribes a free entry ──────────────────────
    _, _, admin_token = await _register_login(
        client, _stub_mailhog, db_session=db_session, make_admin=True
    )
    subject_id, _, subject_token = await _register_login(client, _stub_mailhog)
    free_resp = await client.post(
        "/api/v1/tickets/free",
        json={
            "draw_id": str(draw.id),
            "subject_user_id": str(subject_id),
            "slip_reference": "FE-E2E-2026-07",
        },
        headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert free_resp.status_code == 201, free_resp.text
    assert free_resp.json()["ticket_number"] == 2

    subject_tickets = await client.get(
        "/api/v1/tickets/me",
        headers={"Authorization": f"Bearer {subject_token}"},
    )
    assert len(subject_tickets.json()["items"]) == 1
    assert subject_tickets.json()["items"][0]["entry_source"] == "free"

    # ── audit chain: every event present + linked prev→row hashes ───────
    rows = (
        await db_session.execute(select(AuditLog).order_by(AuditLog.seq))
    ).scalars().all()
    events = [r.event_name for r in rows]

    # Not asserting exact order (three registrations + one operator grant
    # + three flows produce a lot of events); asserting presence + chain.
    for expected in (
        "user.registered",
        "otp.issued",
        "otp.verified",
        "user.password_set",
        "session.created",
        "skill_question.issued",
        "skill_question.answered_correct",
        "payment.intent_created",
        "wallet.ticket_sale_recorded",
        "ticket.issued",
        "ticket.paid_purchase_completed",
        "wallet.payment_fee_posted",
        "payment.confirmed",
        "ticket.free_transcribed",
    ):
        assert expected in events, f"missing event {expected} — got {events}"

    for prev, curr in itertools.pairwise(rows):
        assert curr.prev_hash == prev.row_hash, (
            f"chain break at seq={curr.seq}: prev_hash mismatch"
        )
