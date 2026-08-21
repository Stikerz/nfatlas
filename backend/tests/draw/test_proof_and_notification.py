"""GET /draws/{id}/proof + verifier CLI + winner notification tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.audit_log.models import AuditLog
from atlas.draw import crypto as seed_crypto
from atlas.draw.models import Draw
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


@pytest.fixture
def _stub_notification_sender(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[list[dict[str, str]]]:
    """Capture winner-notification emails without a real Mailhog."""
    sent: list[dict[str, str]] = []

    async def _stub(
        *,
        to_email: str,
        subject: str,
        body: str,
        from_addr: str = "notifications@atlas.dev",
    ) -> None:
        sent.append(
            {"to": to_email, "subject": subject, "body": body, "from": from_addr}
        )

    monkeypatch.setattr(mailhog_sender, "send_notification", _stub)
    yield sent


async def _seed_draw(session: AsyncSession, *, state: str = "sales_open") -> Draw:
    now = datetime.now(UTC)
    draw_id = uuid.uuid4()
    seed = hashlib.sha256(b"proof-seed-" + draw_id.bytes).digest()
    draw = Draw(
        id=draw_id,
        prize_copy="test prize for the proof",
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


async def _mint_tickets(
    session: AsyncSession, *, draw: Draw, count: int
) -> list[uuid.UUID]:
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
            idempotency_key=f"proof-test-{uuid.uuid4()}",
        )
        session.add(ticket)
        await session.flush()
        ids.append(ticket.id)
    await session.commit()
    return ids


async def _close_and_reveal(
    client: AsyncClient, draw_id: uuid.UUID, admin_token: str
) -> None:
    close = await client.post(
        f"/api/v1/draws/{draw_id}/close",
        headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert close.status_code == 200
    reveal = await client.post(
        f"/api/v1/draws/{draw_id}/reveal",
        headers={"Authorization": f"Bearer {admin_token}", "Idempotency-Key": str(uuid.uuid4())},
    )
    assert reveal.status_code == 200


class TestProofPreReveal:
    async def test_returns_minimal_shape(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_notification_sender: list[dict[str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        response = await client.get(f"/api/v1/draws/{draw.id}/proof")
        assert response.status_code == 200
        body = response.json()
        assert body["state"] == "sales_open"
        assert body["commitment"] == draw.commitment
        # Post-reveal fields absent / null.
        assert body["server_seed"] is None
        assert body["tickets_hash"] is None
        assert body["winners"] is None
        assert body["entropy"] is None

    async def test_public_no_auth_required(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_notification_sender: list[dict[str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        response = await client.get(f"/api/v1/draws/{draw.id}/proof")
        assert response.status_code == 200

    async def test_unknown_draw_returns_404(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/draws/{uuid.uuid4()}/proof")
        assert response.status_code == 404


class TestProofPostReveal:
    async def test_returns_full_proof_shape(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
        _stub_notification_sender: list[dict[str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        ticket_ids = await _mint_tickets(db_session, draw=draw, count=6)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await _close_and_reveal(client, draw.id, admin_token)

        response = await client.get(f"/api/v1/draws/{draw.id}/proof")
        assert response.status_code == 200
        body = response.json()

        # Post-reveal fields populated. `server_seed` in the proof is
        # the decrypted seed as hex (public reveal per ADR-006 §Stage 3),
        # not the encrypted-at-rest DB value (W8, ADR-006 §Stage 1).
        assert body["state"] == "revealed"
        assert body["server_seed"] == seed_crypto.decrypt_server_seed(
            draw.server_seed_encrypted
        ).hex()
        assert len(body["server_seed"]) == 64
        assert len(body["tickets_hash"]) == 64
        assert body["ticket_count"] == 6
        assert set(body["ordered_ticket_ids"]) == {str(t) for t in ticket_ids}
        assert body["entropy"]["mode"] == "stub"
        assert len(body["entropy"]["bitcoin_hash"]) == 64
        assert body["algorithm_reference"].startswith("https://")
        assert len(body["winners"]) == 6
        assert body["winners"][0]["is_primary"] is True

    async def test_never_leaks_pii(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
        _stub_notification_sender: list[dict[str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        await _mint_tickets(db_session, draw=draw, count=6)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await _close_and_reveal(client, draw.id, admin_token)

        response = await client.get(f"/api/v1/draws/{draw.id}/proof")
        body_text = response.text
        # No raw user emails.
        assert "@example.com" not in body_text
        assert "@sms-mock.local" not in body_text
        # No raw phones.
        assert "+2348030" not in body_text
        # Winner shape uses user_id_hash, NOT user_id.
        for winner in response.json()["winners"]:
            assert "user_id" not in winner
            assert "user_id_hash" in winner
            assert len(winner["user_id_hash"]) == 64


class TestVerifierCLI:
    """The verifier CLI runs as a subprocess so PATH + argv match a real
    third-party invocation, not an in-process import."""

    def _cli_path(self) -> Path:
        return (
            Path(__file__).resolve().parents[2] / "tools" / "verify_draw.py"
        )

    def test_valid_proof_exits_0(self, tmp_path: Path) -> None:
        """Golden proof: same server_seed + entropy inputs → recomputed
        winners == published winners. `select_winners` is deterministic;
        the CLI is a thin wrapper over it."""
        # Build a hand-crafted proof consistent with select_winners.
        from atlas.draw.reveal import select_winners

        server_seed = b"\x01" * 32
        bitcoin_hash = b"\x02" * 32
        drand_randomness = b"\x03" * 32
        tickets_hash = b"\x04" * 32
        ticket_ids = [
            uuid.UUID(f"00000000-0000-0000-0000-00000000000{i}") for i in range(8)
        ]
        expected = select_winners(
            server_seed=server_seed,
            entropy=bitcoin_hash + drand_randomness,
            tickets_hash=tickets_hash,
            ordered_ticket_ids=ticket_ids,
            reserves=5,
        )

        proof = {
            "state": "revealed",
            "server_seed": server_seed.hex(),
            "tickets_hash": tickets_hash.hex(),
            "ordered_ticket_ids": [str(t) for t in ticket_ids],
            "entropy": {
                "bitcoin_hash": bitcoin_hash.hex(),
                "drand_randomness": drand_randomness.hex(),
            },
            "reserves": 5,
            "winners": [
                {"position": i, "ticket_id": str(t)}
                for i, t in enumerate(expected)
            ],
        }
        proof_path = tmp_path / "proof.json"
        proof_path.write_text(json.dumps(proof))

        result = subprocess.run(
            [sys.executable, str(self._cli_path()), "--proof", str(proof_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "MATCH" in result.stdout

    def test_tampered_proof_exits_1(self, tmp_path: Path) -> None:
        """Same setup but flip one winner ticket_id — verifier should
        catch it."""
        from atlas.draw.reveal import select_winners

        server_seed = b"\x01" * 32
        bitcoin_hash = b"\x02" * 32
        drand_randomness = b"\x03" * 32
        tickets_hash = b"\x04" * 32
        ticket_ids = [
            uuid.UUID(f"00000000-0000-0000-0000-00000000000{i}") for i in range(8)
        ]
        expected = select_winners(
            server_seed=server_seed,
            entropy=bitcoin_hash + drand_randomness,
            tickets_hash=tickets_hash,
            ordered_ticket_ids=ticket_ids,
            reserves=5,
        )
        # Tamper: swap primary with reserve 5.
        published = expected[:]
        published[0], published[5] = published[5], published[0]

        proof = {
            "state": "revealed",
            "server_seed": server_seed.hex(),
            "tickets_hash": tickets_hash.hex(),
            "ordered_ticket_ids": [str(t) for t in ticket_ids],
            "entropy": {
                "bitcoin_hash": bitcoin_hash.hex(),
                "drand_randomness": drand_randomness.hex(),
            },
            "reserves": 5,
            "winners": [
                {"position": i, "ticket_id": str(t)}
                for i, t in enumerate(published)
            ],
        }
        proof_path = tmp_path / "tampered_proof.json"
        proof_path.write_text(json.dumps(proof))

        result = subprocess.run(
            [sys.executable, str(self._cli_path()), "--proof", str(proof_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "MISMATCH" in result.stdout

    def test_pre_reveal_proof_exits_2(self, tmp_path: Path) -> None:
        proof_path = tmp_path / "prereveal.json"
        proof_path.write_text(json.dumps({"state": "sales_open"}))
        result = subprocess.run(
            [sys.executable, str(self._cli_path()), "--proof", str(proof_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "only revealed" in result.stderr


class TestWinnerNotification:
    async def test_reveal_emits_notification_audit_and_sends_email(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
        _stub_notification_sender: list[dict[str, str]],
    ) -> None:
        draw = await _seed_draw(db_session)
        await _mint_tickets(db_session, draw=draw, count=6)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await _close_and_reveal(client, draw.id, admin_token)

        # 6 notifications sent (primary + 5 reserves).
        assert len(_stub_notification_sender) == 6
        primary = _stub_notification_sender[0]
        assert primary["subject"] == "You won a draw"
        assert "primary" in primary["body"]
        reserve = _stub_notification_sender[1]
        assert reserve["subject"] == "You're a reserve winner"
        assert "reserve" in reserve["body"]

        # Audit events (one per winner).
        notif_count = (
            await db_session.execute(
                select(func.count()).select_from(AuditLog).where(
                    AuditLog.event_name == "notification.winner_selected"
                )
            )
        ).scalar_one()
        assert notif_count == 6

    async def test_smtp_failure_does_not_abort_reveal(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def _boom(**_: object) -> None:
            raise RuntimeError("mailhog is down")

        monkeypatch.setattr(mailhog_sender, "send_notification", _boom)

        draw = await _seed_draw(db_session)
        await _mint_tickets(db_session, draw=draw, count=6)
        _, _, admin_token = await _register_login(
            client, _stub_mailhog, db_session=db_session, make_admin=True
        )
        await _close_and_reveal(client, draw.id, admin_token)

        # Reveal still succeeded: winner rows present, state=revealed.
        await db_session.refresh(draw)
        assert draw.state == "revealed"

        # Audit event STILL fires for each winner (audit-log-before-
        # delivery discipline in notify_winner).
        notif_count = (
            await db_session.execute(
                select(func.count()).select_from(AuditLog).where(
                    AuditLog.event_name == "notification.winner_selected"
                )
            )
        ).scalar_one()
        assert notif_count == 6
