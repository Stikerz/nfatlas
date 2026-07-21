"""Payment HTTP routes.

Week 4 surface:
  POST /api/v1/payments/intents            — Day 3
  POST /api/v1/payments/webhooks/paystack  — Day 4

`GET /payments/intents/{id}` (mobile polling) arrives Week 5.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.idempotency.dependency import IdempotencyGuard, idempotency_guard
from atlas.identity.auth import current_session
from atlas.identity.models import Session as SessionRow
from atlas.identity.models import User
from atlas.payment import service as payment_service
from atlas.payment.providers.paystack import PaystackAdapter
from atlas.payment.providers.protocol import InvalidSignatureError
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


@router.post(
    "/webhooks/paystack",
    status_code=status.HTTP_200_OK,
)
async def paystack_webhook(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> Response:
    """Paystack event ingest — signature-gated per ADR-008 §Invariants 2.

    Reads the raw body BEFORE any parsing (FastAPI's json= param would
    parse-then-verify — wrong order). Passes the raw bytes to the
    adapter's verify_webhook which:
      1. Confirms the x-paystack-signature header is present.
      2. Computes HMAC-SHA-512 over the raw body with the shared secret.
      3. Only if match, parses the JSON body and returns a WebhookEvent.

    Signature-fail returns 401 with NO business state change and NO body
    parsing. Successful events dispatch to payment.service.process_webhook_event
    (idempotent by both intent-status guard and ledger idempotency key).
    """
    raw_body = await request.body()
    # httpx / Starlette headers are already normalized to lowercase.
    headers = {k.lower(): v for k, v in request.headers.items()}

    adapter = PaystackAdapter()
    try:
        event = adapter.verify_webhook(raw_body, headers)
    except InvalidSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_signature", "message": str(exc)},
        ) from exc

    await payment_service.process_webhook_event(db, event=event)
    await db.commit()
    return Response(status_code=status.HTTP_200_OK)
