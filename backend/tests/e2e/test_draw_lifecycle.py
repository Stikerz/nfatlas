"""Week 6 exit-gate E2E — create → sell → close → reveal → verify.

Walks the full operator lifecycle: an admin creates a draw via POST
/draws; six users buy tickets end-to-end through the Paystack webhook;
the admin closes and reveals; the public /proof endpoint publishes the
inputs; the standalone verify_draw.py CLI runs against the proof and
reaches the same winner.

If this test regresses, Week 6 is not shippable — regardless of which
per-slice test is green.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import subprocess
import sys
import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.config import get_settings
from atlas.identity import mailhog_sender
from atlas.outbox import worker as outbox_worker
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


@pytest.fixture(autouse=True)
def _stub_notification(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[list[dict[str, str]]]:
    sent: list[dict[str, str]] = []

    async def _stub(
        *,
        to_email: str,
        subject: str,
        body: str,
        from_addr: str = "notifications@atlas.dev",
    ) -> None:
        sent.append({"to": to_email, "subject": subject})

    monkeypatch.setattr(mailhog_sender, "send_notification", _stub)
    yield sent


def _sign(body: bytes) -> str:
    secret = get_settings().paystack_webhook_secret.get_secret_value()
    return hmac.new(
        key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha512
    ).hexdigest()


async def _seed_skill_pool(session: AsyncSession) -> None:
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
                question_id=q.id, option_text="wrong", is_correct=False, display_order=1
            )
        )
    await session.commit()


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
) -> None:
    """Full purchase + signed webhook. Ticket is minted."""
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


async def test_draw_lifecycle_end_to_end(
    client: AsyncClient,
    db_session: AsyncSession,
    _stub_mailhog: list[tuple[str, str, str]],
    _stub_notification: list[dict[str, str]],
    tmp_path: Path,
) -> None:
    """The Week 6 golden flow — CI regression signal for the trust story."""
    await _seed_skill_pool(db_session)

    # ── Admin creates a fresh draw via the API ──────────────────────────
    _, _, admin_token = await _register_login(
        client, _stub_mailhog, db_session=db_session, make_admin=True
    )
    now = datetime.now(UTC)
    create_resp = await client.post(
        "/api/v1/draws",
        json={
            "prize_copy": "E2E — Win a mortgage-free Lagos apartment.",
            "ticket_price_minor": 500_00,
            "close_time": (now + timedelta(hours=2)).isoformat(),
            "draw_time": (now + timedelta(hours=3)).isoformat(),
        },
        headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert create_resp.status_code == 201, create_resp.text
    draw = create_resp.json()
    draw_id = uuid.UUID(draw["id"])
    assert draw["state"] == "sales_open"
    assert len(draw["commitment"]) == 64

    # Public /proof pre-reveal: shows commitment, no server_seed.
    pre_reveal = await client.get(f"/api/v1/draws/{draw_id}/proof")
    assert pre_reveal.status_code == 200
    assert pre_reveal.json()["commitment"] == draw["commitment"]
    assert pre_reveal.json()["server_seed"] is None

    # ── Six users each buy a paid ticket ────────────────────────────────
    for _ in range(6):
        _, email, token = await _register_login(client, _stub_mailhog)
        await _buy_paid_ticket(client, draw_id, token, email)

    # ── Admin closes ────────────────────────────────────────────────────
    close_resp = await client.post(
        f"/api/v1/draws/{draw_id}/close",
        headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert close_resp.status_code == 200
    assert len(close_resp.json()["tickets_hash"]) == 64

    # ── Admin reveals ───────────────────────────────────────────────────
    reveal_resp = await client.post(
        f"/api/v1/draws/{draw_id}/reveal",
        headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert reveal_resp.status_code == 200
    assert reveal_resp.json()["winner_count"] == 6

    # ── Fetch published proof ───────────────────────────────────────────
    proof_resp = await client.get(f"/api/v1/draws/{draw_id}/proof")
    assert proof_resp.status_code == 200
    proof = proof_resp.json()
    assert proof["state"] == "revealed"
    assert len(proof["server_seed"]) == 64
    assert len(proof["winners"]) == 6

    # ── Verifier CLI: run against the proof, confirm the winner ─────────
    proof_path = tmp_path / "e2e_proof.json"
    proof_path.write_text(json.dumps(proof))
    cli_path = (
        Path(__file__).resolve().parents[2] / "tools" / "verify_draw.py"
    )
    result = subprocess.run(
        [sys.executable, str(cli_path), "--proof", str(proof_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "MATCH" in result.stdout

    # The CLI's recomputed primary winner is what the API published.
    winners_resp = await client.get(
        f"/api/v1/draws/{draw_id}/winners",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    api_primary = next(
        w for w in winners_resp.json()["items"] if w["is_primary"]
    )
    assert api_primary["ticket_id"] in result.stdout

    # ── Winner notifications fired via outbox worker (W8 Day 3) ────────
    # Reveal enqueued 6 WINNER_SELECTED_V1 rows; the worker dispatches
    # them to the stubbed mailhog.
    await outbox_worker.run_once(db_session, batch_size=100, max_attempts=10)
    assert len(_stub_notification) == 6
