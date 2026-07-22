"""Draw HTTP routes — read-only in V0.5."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.draw import service as draw_service
from atlas.draw.models import Draw
from atlas.draw.schemas import DrawList, DrawSummary

router = APIRouter(prefix="/api/v1/draws", tags=["draw"])


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
