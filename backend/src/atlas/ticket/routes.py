"""Ticket HTTP routes.

POST /api/v1/tickets/purchase  — auth + Idempotency-Key. Creates a
                                 ticket-purpose payment intent and returns
                                 the checkout URL. Ticket is minted on the
                                 webhook. The skill-question entitlement
                                 gate was removed 2026-11-26 (AMEND-003).
GET  /api/v1/tickets/me         — auth-only. Lists the caller's tickets.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.draw import service as draw_service
from atlas.idempotency.dependency import IdempotencyGuard, idempotency_guard
from atlas.identity import self_exclusion
from atlas.identity.auth import current_session
from atlas.identity.models import Session as SessionRow
from atlas.identity.models import User
from atlas.payment import service as payment_service
from atlas.ticket import service as ticket_service
from atlas.ticket.schemas import (
    PurchaseTicketRequest,
    PurchaseTicketResponse,
    TicketList,
    TicketSummary,
)

router = APIRouter(prefix="/api/v1/tickets", tags=["ticket"])

_PURCHASE = "POST /api/v1/tickets/purchase"


@router.post(
    "/purchase",
    status_code=status.HTTP_201_CREATED,
    response_model=PurchaseTicketResponse,
)
async def purchase(
    body: PurchaseTicketRequest,
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_PURCHASE)),
) -> PurchaseTicketResponse:
    if idempotency.cached_response is not None:
        return PurchaseTicketResponse.model_validate(idempotency.cached_response)

    # ADR-010: refuse before creating a payment intent. The binding check
    # is in ticket.service.issue_paid (the webhook reaches it directly);
    # this one exists so an excluded user never sees a checkout page.
    if await self_exclusion.is_excluded(db, user_id=session.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "self_excluded",
                "message": "This account has been closed and cannot enter draws.",
            },
        )

    # Draw exists + sales_open
    try:
        draw = await draw_service.get(db, draw_id=body.draw_id)
    except draw_service.DrawNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "draw_not_found", "message": "Unknown draw id."},
        ) from exc
    if draw.state != "sales_open":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "draw_not_open", "message": "This draw is not accepting entries."},
        )

    user = await db.get(User, session.user_id)
    assert user is not None  # active session implies existing user

    row = await payment_service.create_intent(
        db,
        user_id=session.user_id,
        user_email=user.email,
        amount_minor=draw.ticket_price_minor,
        method="card",
        description=f"Ticket for draw {draw.id}",
        idempotency_key=idempotency.key,
        purpose="ticket",
        extra_metadata={"draw_id": str(draw.id)},
    )

    response = PurchaseTicketResponse(
        payment_intent_id=row.id,
        vendor_reference=row.vendor_reference or "",
        checkout_url=row.checkout_url,
        amount_minor=row.amount_minor,
        currency=row.currency,
        expires_at=payment_service.checkout_expires_at(row),
    )
    await idempotency.record(
        db,
        status_code=status.HTTP_201_CREATED,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=TicketList,
)
async def my_tickets(
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
) -> TicketList:
    rows = await ticket_service.list_for_user(db, user_id=session.user_id)
    return TicketList(
        items=[
            TicketSummary(
                id=r.id,
                draw_id=r.draw_id,
                ticket_number=r.ticket_number,
                entry_source=r.entry_source,
                issued_at=r.issued_at,
            )
            for r in rows
        ]
    )
