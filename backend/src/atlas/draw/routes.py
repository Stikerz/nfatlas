"""Draw HTTP routes — read-only in V0.5."""

from __future__ import annotations

import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.db import get_session
from atlas.draw import reveal as reveal_algo
from atlas.draw import service as draw_service
from atlas.draw.models import Draw
from atlas.draw.schemas import (
    CreateDrawRequest,
    DrawCloseResponse,
    DrawList,
    DrawProof,
    DrawRevealResponse,
    DrawSummary,
    EntropyProof,
    WinnerList,
    WinnerProof,
    WinnerSummary,
)
from atlas.idempotency.dependency import IdempotencyGuard, idempotency_guard
from atlas.identity.auth import current_session
from atlas.identity.models import Session as SessionRow

router = APIRouter(prefix="/api/v1/draws", tags=["draw"])

_CREATE = "POST /api/v1/draws"
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


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DrawSummary,
)
async def create_draw(
    body: CreateDrawRequest,
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_CREATE)),
) -> DrawSummary:
    if idempotency.cached_response is not None:
        return DrawSummary.model_validate(idempotency.cached_response)

    if not await admin_service.is_superadmin(db, user_id=session.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "operator_role_required",
                "message": "Creating a draw is an operator action.",
            },
        )

    row = await draw_service.create_draw(
        db,
        prize_copy=body.prize_copy,
        ticket_price_minor=body.ticket_price_minor,
        close_time=body.close_time,
        draw_time=body.draw_time,
        entries_cap=body.entries_cap,
        actor_operator_id=session.user_id,
    )
    response = _to_summary(row)
    await idempotency.record(
        db,
        status_code=status.HTTP_201_CREATED,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


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


_ALGORITHM_REF = (
    "https://github.com/Stikerz/nfatlas/blob/main/docs/adr/"
    "ADR-006-commit-reveal-protocol-and-public-entropy.md"
)


@router.get(
    "/{draw_id}/proof",
    status_code=status.HTTP_200_OK,
    response_model=DrawProof,
)
async def get_proof(
    draw_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> DrawProof:
    """PUBLIC (no auth) — the trust surface.

    Pre-reveal: minimal shape (id, state, commitment, close_time,
    draw_time). Post-reveal: full proof so any third party can re-run
    select_winners against these inputs. Never leaks email/phone —
    winner identifiers are SHA-256 hashes of user_id.
    """
    try:
        row = await draw_service.get(db, draw_id=draw_id)
    except draw_service.DrawNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "draw_not_found", "message": "Unknown draw id."},
        ) from exc

    if row.state != "revealed":
        return DrawProof(
            id=row.id,
            state=row.state,
            commitment=row.commitment,
            close_time=row.close_time,
            draw_time=row.draw_time,
        )

    ticket_ids = await draw_service.ordered_ticket_ids(db, draw_id=draw_id)
    winners = await draw_service.list_winners(db, draw_id=draw_id)
    inputs = row.reveal_inputs

    return DrawProof(
        id=row.id,
        state=row.state,
        commitment=row.commitment,
        close_time=row.close_time,
        draw_time=row.draw_time,
        revealed_at=row.revealed_at,
        server_seed=row.server_seed_encrypted,
        tickets_hash=row.tickets_hash,
        ticket_count=len(ticket_ids),
        ordered_ticket_ids=ticket_ids,
        entropy=EntropyProof(
            mode=inputs.get("mode", ""),
            bitcoin_hash=inputs.get("bitcoin_hash", ""),
            bitcoin_height=int(inputs.get("bitcoin_height", 0)),
            bitcoin_timestamp=int(inputs.get("bitcoin_timestamp", 0)),
            drand_round=int(inputs.get("drand_round", 0)),
            drand_randomness=inputs.get("drand_randomness", ""),
            drand_signature=inputs.get("drand_signature", ""),
            verified_at=inputs.get("verified_at", ""),
        ),
        winners=[
            WinnerProof(
                position=w.position,
                is_primary=w.is_primary,
                ticket_id=w.ticket_id,
                user_id_hash=hashlib.sha256(str(w.user_id).encode("utf-8")).hexdigest(),
            )
            for w in winners
        ],
        algorithm_reference=_ALGORITHM_REF,
        reserves=max(0, len(winners) - 1),
    )


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
