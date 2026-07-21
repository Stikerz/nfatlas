"""Identity HTTP routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.db import get_session
from atlas.idempotency.dependency import IdempotencyGuard, idempotency_guard
from atlas.identity import (
    mailhog_sender,
    otp_service,
    password_service,
    session_service,
)
from atlas.identity import (
    service as identity_service,
)
from atlas.identity.auth import current_session
from atlas.identity.models import Session as SessionRow
from atlas.identity.models import User
from atlas.identity.schemas import (
    OTPIssueRequest,
    OTPIssueResponse,
    OTPVerifyRequest,
    OTPVerifyResponse,
    PasswordSetRequest,
    RegisterRequest,
    RegisterResponse,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionCurrentResponse,
)

router = APIRouter(prefix="/api/v1", tags=["identity"])

_REGISTER = "POST /api/v1/users"
_OTP_ISSUE = "POST /api/v1/otps"
_OTP_VERIFY = "POST /api/v1/otps/verify"
_PASSWORD_SET = "POST /api/v1/users/{id}/password"
_SESSION_CREATE = "POST /api/v1/sessions"


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_REGISTER)),
) -> RegisterResponse:
    if idempotency.cached_response is not None:
        return RegisterResponse.model_validate(idempotency.cached_response)
    response = await identity_service.register(db, body)
    await idempotency.record(
        db,
        status_code=status.HTTP_201_CREATED,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.post(
    "/otps",
    status_code=status.HTTP_201_CREATED,
    response_model=OTPIssueResponse,
)
async def issue_otp(
    body: OTPIssueRequest,
    db: AsyncSession = Depends(get_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_OTP_ISSUE)),
) -> OTPIssueResponse:
    if idempotency.cached_response is not None:
        return OTPIssueResponse.model_validate(idempotency.cached_response)

    otp, code = await otp_service.issue(db, user_id=body.user_id, purpose=body.purpose)

    # Look up phone for mailhog wire address.
    from atlas.identity.models import User

    user = await db.get(User, body.user_id)
    assert user is not None  # unknown_user already raised
    await mailhog_sender.send_otp(
        phone_e164=user.phone_e164,
        code=code,
        purpose=body.purpose,
    )

    response = OTPIssueResponse(otp_id=otp.id, expires_at=otp.expires_at)
    await idempotency.record(
        db,
        status_code=status.HTTP_201_CREATED,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.post(
    "/otps/verify",
    status_code=status.HTTP_200_OK,
    response_model=OTPVerifyResponse,
)
async def verify_otp(
    body: OTPVerifyRequest,
    db: AsyncSession = Depends(get_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_OTP_VERIFY)),
) -> OTPVerifyResponse:
    if idempotency.cached_response is not None:
        return OTPVerifyResponse.model_validate(idempotency.cached_response)

    try:
        await otp_service.verify(
            db, user_id=body.user_id, purpose=body.purpose, code=body.code
        )
    except otp_service.OTPVerificationFailed as exc:
        # Persist the otp.verification_failed audit event (plan §5) AND the
        # cached 400 response — retries with the same key get the same 400
        # per ADR-004.
        await idempotency.record(
            db,
            status_code=exc.status_code,
            response_body=exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail},
        )
        await db.commit()
        raise

    response = OTPVerifyResponse(verified=True)
    await idempotency.record(
        db,
        status_code=status.HTTP_200_OK,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.post(
    "/users/{user_id}/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def set_password(
    user_id: uuid.UUID,
    body: PasswordSetRequest,
    db: AsyncSession = Depends(get_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_PASSWORD_SET)),
) -> None:
    if idempotency.cached_response is not None:
        return None

    await password_service.set_password(db, user_id=user_id, plaintext=body.password)
    await idempotency.record(db, status_code=status.HTTP_204_NO_CONTENT, response_body={})
    await db.commit()
    return None


@router.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
    response_model=SessionCreateResponse,
)
async def create_session(
    body: SessionCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
    idempotency: IdempotencyGuard = Depends(idempotency_guard(endpoint=_SESSION_CREATE)),
) -> SessionCreateResponse:
    if idempotency.cached_response is not None:
        return SessionCreateResponse.model_validate(idempotency.cached_response)

    row, token = await session_service.create(
        db,
        email=str(body.email),
        password=body.password,
        ip_addr=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    response = SessionCreateResponse(
        session_id=row.id,
        user_id=row.user_id,
        access_token=token,
        expires_at=row.expires_at,
    )
    await idempotency.record(
        db,
        status_code=status.HTTP_201_CREATED,
        response_body=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.post(
    "/sessions/current/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
) -> None:
    await session_service.revoke_current(db, session_id=session.id)
    await db.commit()
    return None


@router.get(
    "/sessions/current",
    status_code=status.HTTP_200_OK,
    response_model=SessionCurrentResponse,
)
async def get_current_session(
    db: AsyncSession = Depends(get_session),
    session: SessionRow = Depends(current_session),
) -> SessionCurrentResponse:
    user = await db.get(User, session.user_id)
    assert user is not None  # active session implies existing user
    roles = await admin_service.roles_for(db, user_id=session.user_id)
    return SessionCurrentResponse(
        session_id=session.id,
        user_id=session.user_id,
        email=user.email,
        issued_at=session.issued_at,
        expires_at=session.expires_at,
        roles=roles,
        is_admin=admin_service.SUPERADMIN_ROLE in roles,
    )
