"""Skill-question HTTP routes — integration tests through the full stack."""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.draw.models import Draw
from atlas.identity import mailhog_sender
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


async def _seed_draw_and_pool(
    session: AsyncSession, *, size: int = 3
) -> Draw:
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
        state="sales_open",
        commitment=hashlib.sha256(seed + draw_id.bytes).hexdigest(),
        server_seed_encrypted=seed.hex(),
    )
    session.add(draw)
    for i in range(size):
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
    await session.commit()
    return draw


async def _register_and_login(
    client: AsyncClient, sent_stub: list[tuple[str, str, str]]
) -> tuple[uuid.UUID, str]:
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
    return user_id, login.json()["access_token"]


class TestNextQuestionEndpoint:
    async def test_returns_prompt_and_options_no_is_correct(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw_and_pool(db_session)
        _, token = await _register_and_login(client, _stub_mailhog)

        response = await client.get(
            f"/api/v1/draws/{draw.id}/skill-questions/next",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["prompt"].startswith("Question ")
        assert len(body["options"]) == 2
        for opt in body["options"]:
            # Explicit shape check — is_correct MUST NOT be exposed.
            assert set(opt.keys()) == {"id", "text"}

    async def test_returns_409_if_draw_not_open(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw_and_pool(db_session)
        # Reopen via UPDATE — simulate a closed draw.
        from sqlalchemy import update

        await db_session.execute(
            update(Draw).where(Draw.id == draw.id).values(state="sales_closed")
        )
        await db_session.commit()

        _, token = await _register_and_login(client, _stub_mailhog)
        response = await client.get(
            f"/api/v1/draws/{draw.id}/skill-questions/next",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "draw_not_open"

    async def test_unauthenticated_returns_401(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        draw = await _seed_draw_and_pool(db_session)
        response = await client.get(
            f"/api/v1/draws/{draw.id}/skill-questions/next",
        )
        assert response.status_code == 401


class TestAnswerEndpoint:
    async def _next(
        self, client: AsyncClient, draw_id: uuid.UUID, token: str
    ) -> dict:
        response = await client.get(
            f"/api/v1/draws/{draw_id}/skill-questions/next",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text
        return response.json()

    async def test_correct_answer_returns_entitlement(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw_and_pool(db_session)
        _, token = await _register_and_login(client, _stub_mailhog)

        question = await self._next(client, draw.id, token)
        # Look up the correct option by its text — "correct" is the label.
        correct_id = next(o["id"] for o in question["options"] if o["text"] == "correct")

        response = await client.post(
            f"/api/v1/skill-questions/attempts/{question['attempt_id']}/answer",
            json={"option_id": correct_id},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["is_correct"] is True
        assert body["entitlement_expires_at"] is not None

    async def test_wrong_answer_returns_no_entitlement(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw_and_pool(db_session)
        _, token = await _register_and_login(client, _stub_mailhog)

        question = await self._next(client, draw.id, token)
        wrong_id = next(o["id"] for o in question["options"] if o["text"] != "correct")

        response = await client.post(
            f"/api/v1/skill-questions/attempts/{question['attempt_id']}/answer",
            json={"option_id": wrong_id},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_correct"] is False
        assert body["entitlement_expires_at"] is None

    async def test_replay_same_idempotency_key_returns_cached(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw_and_pool(db_session)
        _, token = await _register_and_login(client, _stub_mailhog)

        question = await self._next(client, draw.id, token)
        correct_id = next(o["id"] for o in question["options"] if o["text"] == "correct")
        key = str(uuid.uuid4())

        first = await client.post(
            f"/api/v1/skill-questions/attempts/{question['attempt_id']}/answer",
            json={"option_id": correct_id},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": key},
        )
        second = await client.post(
            f"/api/v1/skill-questions/attempts/{question['attempt_id']}/answer",
            json={"option_id": correct_id},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": key},
        )
        assert first.json() == second.json()

    async def test_re_answer_without_idempotency_key_returns_409(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw_and_pool(db_session)
        _, token = await _register_and_login(client, _stub_mailhog)
        question = await self._next(client, draw.id, token)
        correct_id = next(o["id"] for o in question["options"] if o["text"] == "correct")

        # First submission with one key.
        first = await client.post(
            f"/api/v1/skill-questions/attempts/{question['attempt_id']}/answer",
            json={"option_id": correct_id},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert first.status_code == 200

        # Second submission with a DIFFERENT key — same attempt, so
        # the service raises AlreadyAnsweredError → 409.
        second = await client.post(
            f"/api/v1/skill-questions/attempts/{question['attempt_id']}/answer",
            json={"option_id": correct_id},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert second.status_code == 409
        assert second.json()["detail"]["code"] == "attempt_already_answered"

    async def test_unknown_attempt_returns_404(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, token = await _register_and_login(client, _stub_mailhog)
        response = await client.post(
            f"/api/v1/skill-questions/attempts/{uuid.uuid4()}/answer",
            json={"option_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "attempt_not_found"

    async def test_cross_user_attempt_returns_403(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        draw = await _seed_draw_and_pool(db_session)
        _, token_a = await _register_and_login(client, _stub_mailhog)
        question = await self._next(client, draw.id, token_a)
        correct_id = next(o["id"] for o in question["options"] if o["text"] == "correct")

        _, token_b = await _register_and_login(client, _stub_mailhog)
        response = await client.post(
            f"/api/v1/skill-questions/attempts/{question['attempt_id']}/answer",
            json={"option_id": correct_id},
            headers={"Authorization": f"Bearer {token_b}", "Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "attempt_forbidden"
