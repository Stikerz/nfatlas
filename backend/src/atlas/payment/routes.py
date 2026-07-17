"""Payment HTTP routes (Week 4 surface).

Only `POST /api/v1/payments/intents` lands this week. The Paystack
webhook endpoint arrives Day 4; the `GET /payments/intents/{id}` read
surface arrives with the mobile polling loop in Week 5.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.idempotency.dependency import IdempotencyGuard, idempotency_guard
from atlas.identity.auth import current_session
from atlas.identity.models import Session as SessionRow
from atlas.identity.models import User
from atlas.payment import service as payment_service
from atlas.payment.schemas import CreateIntentRequest, CreateIntentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["payment"])

_CREATE_INTENT = "POST /api/v1/payments/intents"


@router.post(
    "/intents",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateIntentResponse,
)
async def create_intent(
    body: CreateIntentRequest,
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_CREATE_INTENT)),
) -> CreateIntentResponse:
    if idempotency.cached_response is not None:
        return CreateIntentResponse.model_validate(idempotency.cached_response)

    user = await db.get(User, session.user_id)
    assert user is not None  # active session implies existing user

    row = await payment_service.create_intent(
        db,
        user_id=session.user_id,
        user_email=user.email,
        amount_minor=body.amount_minor,
        method=body.method,
        description=body.description,
        idempotency_key=idempotency.key,
    )

    response = CreateIntentResponse(
        payment_intent_id=row.id,
        vendor_reference=row.vendor_reference or "",
        checkout_url=row.checkout_url,
        amount_minor=row.amount_minor,
        currency=row.currency,
        status=row.status,
        expires_at=payment_service.checkout_expires_at(row),
    )
    await idempotency.record(
        db,
        status_code=status.HTTP_201_CREATED,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response
