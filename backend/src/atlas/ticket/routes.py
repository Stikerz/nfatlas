"""Ticket HTTP routes.

POST /api/v1/tickets/purchase  — auth + Idempotency-Key. Validates the
                                 entitlement, creates a ticket-purpose
                                 payment intent, returns checkout URL.
                                 Ticket is minted on the webhook.
GET  /api/v1/tickets/me         — auth-only. Lists the caller's tickets.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.draw import service as draw_service
from atlas.idempotency.dependency import IdempotencyGuard, idempotency_guard
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

    # Entitlement pre-check (fast client feedback; webhook re-checks + consumes)
    try:
        await ticket_service.check_entitlement(
            db,
            entitlement_id=body.entitlement_id,
            expected_user_id=session.user_id,
            expected_draw_id=body.draw_id,
        )
    except ticket_service.EntitlementNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "entitlement_not_found", "message": "Unknown entitlement id."},
        ) from exc
    except ticket_service.EntitlementForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "entitlement_forbidden",
                "message": "This entitlement belongs to another user.",
            },
        ) from exc
    except ticket_service.EntitlementInvalidError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": f"entitlement_{exc.args[0]}",
                "message": (
                    "This entitlement is not usable for this purchase."
                ),
            },
        ) from exc

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
        extra_metadata={
            "draw_id": str(draw.id),
            "entitlement_id": str(body.entitlement_id),
        },
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
