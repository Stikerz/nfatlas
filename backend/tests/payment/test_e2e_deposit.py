"""Week 4 exit-gate E2E — the flagship user-money flow end-to-end.

Walks register → OTP → verify → password → login → create intent →
signed webhook → wallet credit → audit chain intact. This is the
one-test summary of everything Week 4 shipped; a failure here means
Week 4 regressed regardless of what the per-slice tests say.

Distinct from the per-slice webhook tests (which cover edge cases like
bad signatures and unknown vendor refs) — this one is the happy-path
integration and the sanity check for Week 5 (the mobile client will
drive exactly this shape).
"""

from __future__ import annotations

import hashlib
import hmac
import itertools
import json
import uuid
from collections.abc import Iterator
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog
from atlas.config import get_settings
from atlas.identity import mailhog_sender
from atlas.payment.models import PaymentIntentRow
from atlas.payment.providers import paystack_fixtures
from atlas.payment.providers.protocol import PaymentStatus
from atlas.wallet import queries as wallet_queries
from atlas.wallet import service as wallet_service


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


async def test_deposit_e2e_happy_path(
    client: AsyncClient,
    db_session: AsyncSession,
    _stub_mailhog: list[tuple[str, str, str]],
) -> None:
    """The Week 4 golden flow — must stay green through Week 5 refactors."""
    email = f"kemi-{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+2348030{uuid.uuid4().int % 1_000_000:06d}"
    password = "correct horse battery staple"
    deposit_kobo = 1_000_00  # ₦1,000

    # ── register ─────────────────────────────────────────────────────────
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

    # ── OTP issue + verify ───────────────────────────────────────────────
    otp_response = await client.post(
        "/api/v1/otps",
        json={"user_id": str(user_id), "purpose": "registration"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert otp_response.status_code == 201
    code = _stub_mailhog[-1][1]

    verify = await client.post(
        "/api/v1/otps/verify",
        json={"user_id": str(user_id), "purpose": "registration", "code": code},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert verify.status_code == 200

    # ── password set + login ─────────────────────────────────────────────
    pw = await client.post(
        f"/api/v1/users/{user_id}/password",
        json={"password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert pw.status_code == 204

    login = await client.post(
        "/api/v1/sessions",
        json={"email": email, "password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert login.status_code == 201
    token = login.json()["access_token"]

    # ── payment intent ───────────────────────────────────────────────────
    intent_response = await client.post(
        "/api/v1/payments/intents",
        json={"amount_minor": deposit_kobo, "method": "card", "description": "Top-up"},
        headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert intent_response.status_code == 201, intent_response.text
    vendor_ref = intent_response.json()["vendor_reference"]
    assert vendor_ref.startswith("atlas-")
    assert intent_response.json()["checkout_url"].startswith(
        "http://mock-paystack.local/checkout/"
    )

    # ── signed Paystack webhook ─────────────────────────────────────────
    webhook_body = json.dumps(
        paystack_fixtures.charge_success_event(
            reference=vendor_ref, amount_minor=deposit_kobo, email=email
        )
    ).encode("utf-8")
    webhook_response = await client.post(
        "/api/v1/payments/webhooks/paystack",
        content=webhook_body,
        headers={
            "x-paystack-signature": _sign(webhook_body),
            "Content-Type": "application/json",
        },
    )
    assert webhook_response.status_code == 200

    # ── assertion 1: wallet balance ──────────────────────────────────────
    wallet = await wallet_service.get_or_create_user_wallet(db_session, user_id=user_id)
    balance = await wallet_queries.balance_of(db_session, account_id=wallet.id)
    assert balance == deposit_kobo, (
        f"expected wallet to hold {deposit_kobo} kobo, got {balance}"
    )

    # ── assertion 2: intent transitioned to succeeded ────────────────────
    intent_row = (
        await db_session.execute(
            select(PaymentIntentRow).where(
                PaymentIntentRow.vendor_reference == vendor_ref
            )
        )
    ).scalar_one()
    assert intent_row.status == PaymentStatus.SUCCEEDED.value

    # ── assertion 3: full audit chain intact ────────────────────────────
    audit_rows = (
        await db_session.execute(select(AuditLog).order_by(AuditLog.seq))
    ).scalars().all()
    events = [r.event_name for r in audit_rows]
    assert events == [
        "user.registered",
        "otp.issued",
        "otp.verified",
        "user.password_set",
        "session.created",
        "payment.intent_created",
        "wallet.deposit_credited",
        "wallet.payment_fee_posted",
        "payment.confirmed",
    ]
    for prev, curr in itertools.pairwise(audit_rows):
        assert curr.prev_hash == prev.row_hash, (
            f"chain break at seq={curr.seq}: prev_hash mismatch"
        )
