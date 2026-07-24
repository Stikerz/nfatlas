"""Skill-question HTTP routes.

  GET  /api/v1/draws/{draw_id}/skill-questions/next
  POST /api/v1/skill-questions/attempts/{attempt_id}/answer

Both require an authenticated session; the answer route also requires
an Idempotency-Key per ADR-004 (so a network retry after "correct"
returns the cached response instead of a 409 already-answered).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.draw import service as draw_service
from atlas.idempotency.dependency import IdempotencyGuard, idempotency_guard
from atlas.identity.auth import current_session
from atlas.identity.models import Session as SessionRow
from atlas.skill import service as skill_service
from atlas.skill.schemas import (
    AnswerRequest,
    AnswerResponse,
    NextQuestionResponse,
    SkillOption,
)

router = APIRouter(prefix="/api/v1", tags=["skill"])

_ANSWER = "POST /api/v1/skill-questions/attempts/{id}/answer"


@router.get(
    "/draws/{draw_id}/skill-questions/next",
    status_code=status.HTTP_200_OK,
    response_model=NextQuestionResponse,
)
async def next_question(
    draw_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
) -> NextQuestionResponse:
    try:
        result = await skill_service.next_question(
            db, user_id=session.user_id, draw_id=draw_id
        )
    except skill_service.DrawNotOpenForSkillError as exc:
        # 409: the draw exists (or not) but is not accepting entries.
        # This is a state error, not a not-found — a Week 6 closed draw
        # is a 409, not a 404.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "draw_not_open", "message": "This draw is not accepting entries."},
        ) from exc
    except draw_service.DrawNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "draw_not_found", "message": "Unknown draw id."},
        ) from exc
    except skill_service.NoQuestionsAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "no_questions", "message": "No skill questions configured."},
        ) from exc

    await db.commit()
    return NextQuestionResponse(
        attempt_id=result.attempt_id,
        question_id=result.question_id,
        prompt=result.prompt,
        options=[SkillOption(id=oid, text=text) for oid, text in result.options],
        expires_at=result.expires_at,
    )


@router.post(
    "/skill-questions/attempts/{attempt_id}/answer",
    status_code=status.HTTP_200_OK,
    response_model=AnswerResponse,
)
async def answer(
    attempt_id: uuid.UUID,
    body: AnswerRequest,
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_ANSWER)),
) -> AnswerResponse:
    if idempotency.cached_response is not None:
        return AnswerResponse.model_validate(idempotency.cached_response)

    try:
        attempt = await skill_service.verify_answer(
            db,
            attempt_id=attempt_id,
            user_id=session.user_id,
            option_id=body.option_id,
        )
    except skill_service.AttemptNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "attempt_not_found", "message": "Unknown attempt id."},
        ) from exc
    except skill_service.AttemptForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "attempt_forbidden", "message": "This attempt belongs to another user."},
        ) from exc
    except skill_service.AttemptExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={"code": "attempt_expired", "message": "This attempt window has closed. Request a new question."},
        ) from exc
    except skill_service.AttemptAlreadyAnsweredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "attempt_already_answered", "message": "This attempt was already graded."},
        ) from exc
    except skill_service.OptionNotForQuestionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "option_mismatch", "message": "That option is not part of this question."},
        ) from exc

    response = AnswerResponse(
        attempt_id=attempt.id,
        is_correct=bool(attempt.is_correct),
        entitlement_expires_at=attempt.entitlement_expires_at,
    )
    await idempotency.record(
        db,
        status_code=status.HTTP_200_OK,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response
