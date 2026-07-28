"""Draw HTTP routes — read-only in V0.5."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.db import get_session
from atlas.draw import reveal as reveal_algo
from atlas.draw import service as draw_service
from atlas.draw.models import Draw
from atlas.draw.schemas import (
    DrawCloseResponse,
    DrawList,
    DrawRevealResponse,
    DrawSummary,
    WinnerList,
    WinnerSummary,
)
from atlas.idempotency.dependency import IdempotencyGuard, idempotency_guard
from atlas.identity.auth import current_session
from atlas.identity.models import Session as SessionRow

router = APIRouter(prefix="/api/v1/draws", tags=["draw"])

_CLOSE = "POST /api/v1/draws/{id}/close"
_REVEAL = "POST /api/v1/draws/{id}/reveal"


def _to_summary(row: Draw) -> DrawSummary:
    return DrawSummary(
        id=row.id,
        prize_copy=row.prize_copy,
        ticket_price_minor=row.ticket_price_minor,
        currency=row.currency,
        close_time=row.close_time,
        draw_time=row.draw_time,
        state=row.state,
        commitment=row.commitment,
    )


@router.get("", response_model=DrawList)
async def list_draws(
    db: AsyncSession = Depends(get_session),
) -> DrawList:
    rows = await draw_service.list_active(db)
    return DrawList(items=[_to_summary(r) for r in rows])


@router.get("/{draw_id}", response_model=DrawSummary)
async def get_draw(
    draw_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> DrawSummary:
    try:
        row = await draw_service.get(db, draw_id=draw_id)
    except draw_service.DrawNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "draw_not_found", "message": "Unknown draw id."},
        ) from exc
    return _to_summary(row)


@router.post(
    "/{draw_id}/close",
    status_code=status.HTTP_200_OK,
    response_model=DrawCloseResponse,
)
async def close_draw(
    draw_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_CLOSE)),
) -> DrawCloseResponse:
    if idempotency.cached_response is not None:
        return DrawCloseResponse.model_validate(idempotency.cached_response)

    if not await admin_service.is_superadmin(db, user_id=session.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "operator_role_required",
                "message": "Closing a draw is an operator action.",
            },
        )

    try:
        row = await draw_service.close_draw(db, draw_id=draw_id)
    except draw_service.DrawNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "draw_not_found", "message": "Unknown draw id."},
        ) from exc
    except draw_service.DrawStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "draw_state_error", "message": str(exc)},
        ) from exc

    response = DrawCloseResponse(
        id=row.id,
        state=row.state,
        tickets_hash=row.tickets_hash or "",
        close_time=row.close_time,
        draw_time=row.draw_time,
    )
    await idempotency.record(
        db,
        status_code=status.HTTP_200_OK,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.post(
    "/{draw_id}/reveal",
    status_code=status.HTTP_200_OK,
    response_model=DrawRevealResponse,
)
async def reveal_draw(
    draw_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_REVEAL)),
) -> DrawRevealResponse:
    if idempotency.cached_response is not None:
        return DrawRevealResponse.model_validate(idempotency.cached_response)

    if not await admin_service.is_superadmin(db, user_id=session.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "operator_role_required",
                "message": "Revealing a draw is an operator action.",
            },
        )

    try:
        row = await draw_service.reveal_draw(db, draw_id=draw_id)
    except draw_service.DrawNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "draw_not_found", "message": "Unknown draw id."},
        ) from exc
    except draw_service.DrawStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "draw_state_error", "message": str(exc)},
        ) from exc
    except reveal_algo.NotEnoughTicketsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "not_enough_tickets",
                "message": (
                    "This draw does not have enough tickets to satisfy "
                    "the reserve count."
                ),
            },
        ) from exc

    winners = await draw_service.list_winners(db, draw_id=draw_id)
    # revealed_at is set by reveal_draw when it transitions state; the
    # None branch can only happen if the state guard is bypassed.
    assert row.revealed_at is not None
    response = DrawRevealResponse(
        id=row.id,
        state=row.state,
        revealed_at=row.revealed_at,
        winner_count=len(winners),
    )
    await idempotency.record(
        db,
        status_code=status.HTTP_200_OK,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.get(
    "/{draw_id}/winners",
    status_code=status.HTTP_200_OK,
    response_model=WinnerList,
)
async def get_winners(
    draw_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
) -> WinnerList:
    # 404 if the draw itself doesn't exist — otherwise empty list is
    # ambiguous between "no reveal yet" and "unknown draw".
    try:
        await draw_service.get(db, draw_id=draw_id)
    except draw_service.DrawNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "draw_not_found", "message": "Unknown draw id."},
        ) from exc

    rows = await draw_service.list_winners(db, draw_id=draw_id)
    return WinnerList(
        items=[
            WinnerSummary(
                position=r.position,
                is_primary=r.is_primary,
                ticket_id=r.ticket_id,
                user_id=r.user_id,
                contact_status=r.contact_status,
            )
            for r in rows
        ]
    )
