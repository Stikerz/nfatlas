"""Identity HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.identity import service as identity_service
from atlas.identity.schemas import RegisterRequest, RegisterResponse
from atlas.idempotency.dependency import IdempotencyGuard, idempotency_guard

router = APIRouter(prefix="/api/v1", tags=["identity"])

_REGISTER_ENDPOINT = "POST /api/v1/users"


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_REGISTER_ENDPOINT)),
) -> RegisterResponse:
    if idempotency.cached_response is not None:
        return RegisterResponse.model_validate(idempotency.cached_response)

    response = await identity_service.register(session, body)
    await idempotency.record(
        session,
        status_code=status.HTTP_201_CREATED,
        response_body=response.model_dump(mode="json"),
    )
    await session.commit()
    return response
