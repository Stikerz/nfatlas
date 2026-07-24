"""Skill-question service — rotation determinism + verify semantics.

Unit-level tests that go directly through the service module (no HTTP
round-trip). Routes are covered separately in test_skill_routes.py.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog
from atlas.draw.models import Draw
from atlas.identity.models import User
from atlas.skill import service as skill_service
from atlas.skill.models import (
    SkillQuestion,
    SkillQuestionAttempt,
    SkillQuestionOption,
)


async def _make_user(session: AsyncSession) -> uuid.UUID:
    user = User(
        email=f"kemi-{uuid.uuid4().hex[:8]}@example.com",
        phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
        date_of_birth=date(1993, 3, 12),
        status="active",
    )
    session.add(user)
    await session.flush()
    return user.id


async def _make_draw(session: AsyncSession, *, state: str = "sales_open") -> Draw:
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
    await session.flush()
    return draw


async def _seed_question(
    session: AsyncSession, *, prompt: str, correct: str, wrong: list[str]
) -> SkillQuestion:
    q = SkillQuestion(prompt=prompt)
    session.add(q)
    await session.flush()

    session.add(
        SkillQuestionOption(
            question_id=q.id, option_text=correct, is_correct=True, display_order=0
        )
    )
    for i, text in enumerate(wrong, start=1):
        session.add(
            SkillQuestionOption(
                question_id=q.id, option_text=text, is_correct=False, display_order=i
            )
        )
    await session.flush()
    return q


async def _seed_pool(session: AsyncSession, *, size: int = 5) -> list[SkillQuestion]:
    return [
        await _seed_question(
            session,
            prompt=f"Question {i}",
            correct=f"answer-{i}",
            wrong=[f"wrong-{i}-a", f"wrong-{i}-b"],
        )
        for i in range(size)
    ]


class TestNextQuestionRotation:
    async def test_same_minute_same_user_same_question(
        self, db_session: AsyncSession
    ) -> None:
        user_id = await _make_user(db_session)
        draw = await _make_draw(db_session)
        await _seed_pool(db_session, size=5)
        await db_session.commit()

        first = await skill_service.next_question(
            db_session, user_id=user_id, draw_id=draw.id
        )
        second = await skill_service.next_question(
            db_session, user_id=user_id, draw_id=draw.id
        )
        assert first.question_id == second.question_id
        # Different attempts though — new row per call.
        assert first.attempt_id != second.attempt_id

    async def test_different_minute_may_rotate(
        self, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Force two different bucket values and confirm rotation is
        deterministic per (user, draw, bucket) — different buckets should
        (with high probability across a pool of 5) produce different
        questions. Using two hand-picked buckets keeps this a golden test."""
        user_id = await _make_user(db_session)
        draw = await _make_draw(db_session)
        await _seed_pool(db_session, size=5)
        await db_session.commit()

        # Grab the ordered pool to compute expected slots.
        pool = sorted(
            (
                await db_session.execute(
                    __import__("sqlalchemy").select(SkillQuestion.id).order_by(SkillQuestion.id)
                )
            ).scalars().all()
        )
        # Confirm rotation math directly — the private helper is the
        # source of truth for rotation across bucket boundaries.
        b1 = skill_service._rotation_offset(
            user_id=user_id, draw_id=draw.id, bucket=100, pool_size=len(pool)
        )
        b2 = skill_service._rotation_offset(
            user_id=user_id, draw_id=draw.id, bucket=200, pool_size=len(pool)
        )
        # Deterministic values → same call reproduces them.
        assert (
            skill_service._rotation_offset(
                user_id=user_id, draw_id=draw.id, bucket=100, pool_size=len(pool)
            )
            == b1
        )
        # And with sensible bucket spread the offsets are distinct
        # for at least one such pair; if the whole HMAC space collapses
        # to a single slot for this user, the test surfaces it as a real
        # signal rather than a flake.
        assert b1 != b2 or b1 != skill_service._rotation_offset(
            user_id=user_id, draw_id=draw.id, bucket=300, pool_size=len(pool)
        )

    async def test_different_users_may_get_different_questions(
        self, db_session: AsyncSession
    ) -> None:
        """Two different users in the same minute — rotation MUST vary
        deterministically per user_id or else everyone gets the same
        question at the same time (a coordination signal).

        Sample size 20 vs pool size 5 → failure probability (1/5)^19 ≈
        2e-14 assuming a well-behaved HMAC. If this test does fail, the
        signal is a broken rotation function, not a flake."""
        pool_size = 5
        offsets = set()
        for _ in range(20):
            uid = uuid.uuid4()
            offsets.add(
                skill_service._rotation_offset(
                    user_id=uid, draw_id=uuid.uuid4(), bucket=42, pool_size=pool_size
                )
            )
        assert len(offsets) >= 2, "rotation should vary across users"

    async def test_raises_when_draw_not_open(
        self, db_session: AsyncSession
    ) -> None:
        user_id = await _make_user(db_session)
        draw = await _make_draw(db_session, state="draft")
        await _seed_pool(db_session, size=3)
        await db_session.commit()

        with pytest.raises(skill_service.DrawNotOpenForSkillError):
            await skill_service.next_question(
                db_session, user_id=user_id, draw_id=draw.id
            )

    async def test_raises_when_pool_empty(
        self, db_session: AsyncSession
    ) -> None:
        user_id = await _make_user(db_session)
        draw = await _make_draw(db_session)
        await db_session.commit()

        with pytest.raises(skill_service.NoQuestionsAvailableError):
            await skill_service.next_question(
                db_session, user_id=user_id, draw_id=draw.id
            )

    async def test_emits_issued_audit_event(
        self, db_session: AsyncSession
    ) -> None:
        from sqlalchemy import select

        user_id = await _make_user(db_session)
        draw = await _make_draw(db_session)
        await _seed_pool(db_session, size=3)
        await db_session.commit()

        result = await skill_service.next_question(
            db_session, user_id=user_id, draw_id=draw.id
        )
        await db_session.commit()

        event = (
            await db_session.execute(
                select(AuditLog).where(AuditLog.event_name == "skill_question.issued")
            )
        ).scalar_one()
        assert event.payload["user_id"] == str(user_id)
        assert event.subject_id == str(result.attempt_id)


class TestVerifyAnswer:
    async def _issue(
        self, db_session: AsyncSession
    ) -> tuple[uuid.UUID, uuid.UUID, list[SkillQuestionOption]]:
        """Helper: issue an attempt and return (user_id, attempt_id, options)."""
        from sqlalchemy import select

        user_id = await _make_user(db_session)
        draw = await _make_draw(db_session)
        await _seed_pool(db_session, size=3)
        await db_session.commit()

        result = await skill_service.next_question(
            db_session, user_id=user_id, draw_id=draw.id
        )
        await db_session.commit()
        options = (
            await db_session.execute(
                select(SkillQuestionOption).where(
                    SkillQuestionOption.question_id == result.question_id
                )
            )
        ).scalars().all()
        return user_id, result.attempt_id, list(options)

    async def test_correct_answer_grants_entitlement(
        self, db_session: AsyncSession
    ) -> None:
        user_id, attempt_id, options = await self._issue(db_session)
        correct = next(o for o in options if o.is_correct)

        attempt = await skill_service.verify_answer(
            db_session,
            attempt_id=attempt_id,
            user_id=user_id,
            option_id=correct.id,
        )
        await db_session.commit()

        assert attempt.is_correct is True
        assert attempt.answered_at is not None
        assert attempt.entitlement_expires_at is not None
        assert attempt.entitlement_expires_at > datetime.now(UTC)

    async def test_wrong_answer_no_entitlement(
        self, db_session: AsyncSession
    ) -> None:
        user_id, attempt_id, options = await self._issue(db_session)
        wrong = next(o for o in options if not o.is_correct)

        attempt = await skill_service.verify_answer(
            db_session,
            attempt_id=attempt_id,
            user_id=user_id,
            option_id=wrong.id,
        )
        await db_session.commit()

        assert attempt.is_correct is False
        assert attempt.entitlement_expires_at is None

    async def test_cross_user_access_raises(
        self, db_session: AsyncSession
    ) -> None:
        _, attempt_id, options = await self._issue(db_session)
        other_user = await _make_user(db_session)
        await db_session.commit()

        with pytest.raises(skill_service.AttemptForbiddenError):
            await skill_service.verify_answer(
                db_session,
                attempt_id=attempt_id,
                user_id=other_user,
                option_id=options[0].id,
            )

    async def test_already_answered_raises(
        self, db_session: AsyncSession
    ) -> None:
        user_id, attempt_id, options = await self._issue(db_session)
        await skill_service.verify_answer(
            db_session, attempt_id=attempt_id, user_id=user_id, option_id=options[0].id
        )
        await db_session.commit()

        with pytest.raises(skill_service.AttemptAlreadyAnsweredError):
            await skill_service.verify_answer(
                db_session,
                attempt_id=attempt_id,
                user_id=user_id,
                option_id=options[0].id,
            )

    async def test_expired_attempt_raises(
        self, db_session: AsyncSession
    ) -> None:
        from sqlalchemy import update

        user_id, attempt_id, options = await self._issue(db_session)
        # Fast-forward the attempt's expiry into the past.
        await db_session.execute(
            update(SkillQuestionAttempt)
            .where(SkillQuestionAttempt.id == attempt_id)
            .values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )
        await db_session.commit()

        with pytest.raises(skill_service.AttemptExpiredError):
            await skill_service.verify_answer(
                db_session,
                attempt_id=attempt_id,
                user_id=user_id,
                option_id=options[0].id,
            )

    async def test_option_from_other_question_raises(
        self, db_session: AsyncSession
    ) -> None:
        user_id, attempt_id, _ = await self._issue(db_session)
        # Insert a foreign option belonging to a fresh question.
        foreign_q = await _seed_question(
            db_session, prompt="Foreign", correct="ok", wrong=["nope"]
        )
        await db_session.commit()
        from sqlalchemy import select

        foreign_option = (
            await db_session.execute(
                select(SkillQuestionOption).where(
                    SkillQuestionOption.question_id == foreign_q.id
                )
            )
        ).scalars().first()

        with pytest.raises(skill_service.OptionNotForQuestionError):
            await skill_service.verify_answer(
                db_session,
                attempt_id=attempt_id,
                user_id=user_id,
                option_id=foreign_option.id,
            )
