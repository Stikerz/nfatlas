"""Session create / read / revoke.

JWT HS256 with 8h TTL (founder decision 2026-07-13 §0.4). The JWT `jti`
matches the sessions.id column so revocation is enforceable server-side
even though HS256 tokens are self-contained.

Session refresh + rotation is deferred to V1 (plan §10).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.config import get_settings
from atlas.identity.models import Session, User
from atlas.identity.password_service import InvalidCredentials, verify_password

JWT_ALG = "HS256"
JWT_ISSUER = "atlas"


class SessionRevoked(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "session_revoked", "message": "Session is no longer valid."},
        )


class SessionInvalid(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "session_invalid", "message": "Missing or malformed session."},
        )


def _encode_jwt(*, session_id: uuid.UUID, user_id: uuid.UUID, expires_at: datetime) -> str:
    settings = get_settings()
    payload = {
        "iss": JWT_ISSUER,
        "sub": str(user_id),
        "jti": str(session_id),
        "iat": int(datetime.now(UTC).timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.jwt_signing_key.get_secret_value(),
        algorithm=JWT_ALG,
    )


def decode_jwt(token: str) -> dict[str, str | int]:
    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_signing_key.get_secret_value(),
        algorithms=[JWT_ALG],
        issuer=JWT_ISSUER,
        options={"require": ["iss", "sub", "jti", "iat", "exp"]},
    )


async def create(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    ip_addr: str | None,
    user_agent: str | None,
) -> tuple[Session, str]:
    user = (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if user is None or user.password_hash is None:
        raise InvalidCredentials()
    if user.status != "active":
        raise InvalidCredentials()
    if not verify_password(password, user.password_hash):
        raise InvalidCredentials()

    settings = get_settings()
    now = datetime.now(UTC)
    expires_at = now + timedelta(hours=settings.session_ttl_hours)

    row = Session(
        user_id=user.id,
        expires_at=expires_at,
        ip_addr=ip_addr,
        user_agent=user_agent,
    )
    db.add(row)
    await db.flush()

    token = _encode_jwt(session_id=row.id, user_id=user.id, expires_at=expires_at)

    await audit.append(
        db,
        actor_type="user",
        actor_id=str(user.id),
        event_name="session.created",
        subject_type="user",
        subject_id=str(user.id),
        payload={
            "user_id": str(user.id),
            "session_id": str(row.id),
            "ip_addr": ip_addr,
            "user_agent": user_agent,
        },
    )
    return row, token


async def revoke_current(
    db: AsyncSession, *, session_id: uuid.UUID, revoked_by: str = "user"
) -> None:
    row = await db.get(Session, session_id)
    if row is None:
        raise SessionInvalid()
    if row.revoked_at is not None:
        return  # idempotent — already revoked
    row.revoked_at = datetime.now(UTC)
    await db.flush()

    await audit.append(
        db,
        actor_type="user",
        actor_id=str(row.user_id),
        event_name="session.revoked",
        subject_type="user",
        subject_id=str(row.user_id),
        payload={
            "user_id": str(row.user_id),
            "session_id": str(row.id),
            "revoked_by": revoked_by,
        },
    )


async def load_active(
    db: AsyncSession, *, session_id: uuid.UUID
) -> Session:
    row = await db.get(Session, session_id)
    if row is None:
        raise SessionInvalid()
    if row.revoked_at is not None:
        raise SessionRevoked()
    if row.expires_at <= datetime.now(UTC):
        raise SessionRevoked()
    return row
