"""Skill-question service — rotation + verify + entitlement.

Rotation: `next_question` picks a question deterministically from the
active pool using `HMAC-SHA-256(otp_pepper, user_id || draw_id ||
minute_bucket) % pool_size`. Same user / same draw / same minute →
same question. Rationale: prevents "click refresh until an easy one
comes up" without letting the operator hand-pick a hard one.

Answer: `verify_answer` takes the attempt id + chosen option id.
Ownership is checked (attempt.user_id must equal the session user_id;
the route enforces this via a service param). On correct, sets
`entitlement_expires_at = now + ENTITLEMENT_TTL` — Day 3's ticket
purchase route consumes the attempt as an entitlement against this
expiry. On wrong, the attempt is closed but no entitlement is issued;
the user can request a new question.

Audit: emits skill_question.issued on next_question, and
skill_question.answered_correct / .answered_wrong on verify_answer.

Ownership boundary: `next_question` and `verify_answer` are the sole
writers to skill_question_attempts. Day 3's ticket-purchase path
reads the row + marks `consumed_at`. CI grep can add this invariant
later — for W5 the module is small enough to eyeball.
"""

from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import UTC, datetime, timedelta
from typing import NamedTuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.config import get_settings
from atlas.draw import service as draw_service
from atlas.skill.models import (
    SkillQuestion,
    SkillQuestionAttempt,
    SkillQuestionOption,
)

# Time the client has to answer the question after it's issued. Longer
# than the entitlement TTL because a slow user shouldn't be forced to
# re-fetch a question mid-typing.
ATTEMPT_TTL = timedelta(minutes=10)

# After a correct answer, the entitlement is valid for this long to be
# redeemed against a ticket purchase. 5 minutes covers Paystack checkout
# session establishment without leaving stale entitlements around.
ENTITLEMENT_TTL = timedelta(minutes=5)


class QuestionForClient(NamedTuple):
    """Shape returned to the client on next_question — no is_correct."""

    attempt_id: uuid.UUID
    question_id: uuid.UUID
    prompt: str
    options: list[tuple[uuid.UUID, str]]  # (option_id, option_text)
    expires_at: datetime


class DrawNotOpenForSkillError(RuntimeError):
    """next_question called against a draw not in sales_open."""


class NoQuestionsAvailableError(RuntimeError):
    """The active skill_questions pool is empty."""


class AttemptNotFoundError(LookupError):
    """attempt_id unknown."""


class AttemptForbiddenError(PermissionError):
    """attempt.user_id != current session user_id."""


class AttemptExpiredError(RuntimeError):
    """attempt.expires_at is in the past."""


class AttemptAlreadyAnsweredError(RuntimeError):
    """attempt.answered_at is not null — cannot re-answer."""


class OptionNotForQuestionError(ValueError):
    """option_id does not belong to attempt.question_id."""


def _minute_bucket(now: datetime) -> int:
    """Integer minutes since epoch. Used as the rotation bucket."""
    return int(now.timestamp() // 60)


def _rotation_offset(*, user_id: uuid.UUID, draw_id: uuid.UUID, bucket: int, pool_size: int) -> int:
    """HMAC-SHA-256 keyed on the OTP pepper (shared HMAC material per
    ADR-012); output modulo pool size gives a deterministic offset."""
    pepper = get_settings().otp_pepper.get_secret_value().encode("utf-8")
    msg = f"{user_id}|{draw_id}|{bucket}".encode()
    digest = hmac.new(pepper, msg, hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big") % pool_size


async def next_question(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    draw_id: uuid.UUID,
) -> QuestionForClient:
    """Issue a new attempt for user + draw. Same user / same minute →
    same question (see module docstring)."""
    if not await draw_service.is_sales_open(session, draw_id=draw_id):
        raise DrawNotOpenForSkillError(str(draw_id))

    # Ordered pool — must be stable across queries so rotation math
    # picks the same slot as long as pool membership is unchanged.
    question_ids = (
        await session.execute(
            select(SkillQuestion.id)
            .where(SkillQuestion.active.is_(True))
            .order_by(SkillQuestion.id)
        )
    ).scalars().all()
    pool_size = len(question_ids)
    if pool_size == 0:
        raise NoQuestionsAvailableError("no active skill questions in the pool")

    now = datetime.now(UTC)
    offset = _rotation_offset(
        user_id=user_id,
        draw_id=draw_id,
        bucket=_minute_bucket(now),
        pool_size=pool_size,
    )
    question_id = question_ids[offset]

    prompt = (
        await session.execute(
            select(SkillQuestion.prompt).where(SkillQuestion.id == question_id)
        )
    ).scalar_one()
    options = (
        await session.execute(
            select(SkillQuestionOption.id, SkillQuestionOption.option_text)
            .where(SkillQuestionOption.question_id == question_id)
            .order_by(SkillQuestionOption.display_order, SkillQuestionOption.id)
        )
    ).all()

    attempt = SkillQuestionAttempt(
        user_id=user_id,
        draw_id=draw_id,
        question_id=question_id,
        expires_at=now + ATTEMPT_TTL,
    )
    session.add(attempt)
    await session.flush()

    await audit.append(
        session,
        actor_type="user",
        actor_id=str(user_id),
        event_name="skill_question.issued",
        subject_type="skill_question_attempt",
        subject_id=str(attempt.id),
        payload={
            "user_id": str(user_id),
            "draw_id": str(draw_id),
            "question_id": str(question_id),
            "expires_at": attempt.expires_at.isoformat(),
        },
    )

    return QuestionForClient(
        attempt_id=attempt.id,
        question_id=question_id,
        prompt=prompt,
        options=[(row[0], row[1]) for row in options],
        expires_at=attempt.expires_at,
    )


async def verify_answer(
    session: AsyncSession,
    *,
    attempt_id: uuid.UUID,
    user_id: uuid.UUID,
    option_id: uuid.UUID,
) -> SkillQuestionAttempt:
    """Grade a submitted answer. Returns the updated attempt row.

    - AttemptNotFoundError on unknown attempt_id.
    - AttemptForbiddenError if the attempt belongs to a different user.
    - AttemptExpiredError if the attempt's ATTEMPT_TTL window is past.
    - AttemptAlreadyAnsweredError if already answered (route caller may
      still return the cached decision via idempotency layer).
    - OptionNotForQuestionError if the option belongs to a different
      question — treated as a client bug, not a wrong answer.
    """
    attempt = await session.get(SkillQuestionAttempt, attempt_id)
    if attempt is None:
        raise AttemptNotFoundError(str(attempt_id))
    if attempt.user_id != user_id:
        raise AttemptForbiddenError(str(attempt_id))

    now = datetime.now(UTC)
    if attempt.answered_at is not None:
        raise AttemptAlreadyAnsweredError(str(attempt_id))
    if attempt.expires_at <= now:
        raise AttemptExpiredError(str(attempt_id))

    option = await session.get(SkillQuestionOption, option_id)
    if option is None or option.question_id != attempt.question_id:
        raise OptionNotForQuestionError(str(option_id))

    attempt.answered_at = now
    attempt.is_correct = bool(option.is_correct)
    if attempt.is_correct:
        attempt.entitlement_expires_at = now + ENTITLEMENT_TTL

    await audit.append(
        session,
        actor_type="user",
        actor_id=str(user_id),
        event_name=(
            "skill_question.answered_correct"
            if attempt.is_correct
            else "skill_question.answered_wrong"
        ),
        subject_type="skill_question_attempt",
        subject_id=str(attempt.id),
        payload={
            "user_id": str(user_id),
            "draw_id": str(attempt.draw_id),
            "question_id": str(attempt.question_id),
            "option_id": str(option_id),
            "entitlement_expires_at": (
                attempt.entitlement_expires_at.isoformat()
                if attempt.entitlement_expires_at
                else None
            ),
        },
    )
    await session.flush()
    return attempt
