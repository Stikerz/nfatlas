"""OTP issue + verify.

Discipline:
- Code generation: 6 digits, cryptographically random (secrets.randbelow).
- Code storage: HMAC-SHA-256(otp_pepper, code) — plaintext never persisted.
- TTL: 10 minutes from issue.
- Rate limit: at most 1 OTP per 60 seconds per (user, purpose), and at most
  3 OTPs per rolling hour per (user, purpose). Enforced by counting recent
  rows before insert.
- Verify: single-use (sets consumed_at); wrong/expired/consumed returns 400
  with a machine-readable reason and writes otp.verification_failed audit.

Not in scope this week: 3-strike lockout + cooldown per user (plan §1
non-goals). Adding would require an attempts counter on the user row.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.config import get_settings
from atlas.identity.models import OTP, User

OTP_LENGTH = 6
OTP_TTL = timedelta(minutes=10)
RESEND_INTERVAL = timedelta(seconds=60)
HOURLY_MAX = 3
HOURLY_WINDOW = timedelta(hours=1)


class UnknownUser(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "unknown_user", "message": "User not found."},
        )


class RateLimited(HTTPException):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": code, "message": message},
            headers={"Retry-After": "60"},
        )


class OTPVerificationFailed(HTTPException):
    def __init__(self, reason: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "otp_verification_failed",
                "reason": reason,
                "message": f"OTP verification failed: {reason}.",
            },
        )


def _generate_code() -> str:
    """Six ASCII digits, cryptographically random."""
    return f"{secrets.randbelow(10**OTP_LENGTH):0{OTP_LENGTH}d}"


def _hash_code(code: str) -> str:
    pepper = get_settings().otp_pepper.get_secret_value().encode("utf-8")
    return hmac.new(pepper, code.encode("utf-8"), hashlib.sha256).hexdigest()


def _now() -> datetime:
    return datetime.now(UTC)


async def issue(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    purpose: str,
) -> tuple[OTP, str]:
    """Issue an OTP for the user. Returns (record, plaintext_code).

    Plaintext code is returned so the caller can dispatch it (mailhog in V0.5,
    real SMS later). The code is never persisted.
    """
    user = await session.get(User, user_id)
    if user is None:
        raise UnknownUser()

    now = _now()

    last_issued_at = (
        await session.execute(
            select(func.max(OTP.issued_at)).where(
                OTP.user_id == user_id,
                OTP.purpose == purpose,
            )
        )
    ).scalar_one_or_none()
    if last_issued_at is not None and now - last_issued_at < RESEND_INTERVAL:
        raise RateLimited(
            "otp_resend_too_soon",
            "Wait at least 60 seconds before requesting another code.",
        )

    hourly_count = (
        await session.execute(
            select(func.count()).where(
                OTP.user_id == user_id,
                OTP.purpose == purpose,
                OTP.issued_at >= now - HOURLY_WINDOW,
            )
        )
    ).scalar_one()
    if hourly_count >= HOURLY_MAX:
        raise RateLimited(
            "otp_hourly_limit",
            f"Reached {HOURLY_MAX} OTPs in the last hour. Try again later.",
        )

    code = _generate_code()
    otp = OTP(
        user_id=user_id,
        code_hash=_hash_code(code),
        channel="mailhog",
        purpose=purpose,
        expires_at=now + OTP_TTL,
    )
    session.add(otp)
    await session.flush()

    await audit.append(
        session,
        actor_type="user",
        actor_id=str(user_id),
        event_name="otp.issued",
        subject_type="user",
        subject_id=str(user_id),
        payload={
            "user_id": str(user_id),
            "otp_id": str(otp.id),
            "channel": otp.channel,
            "purpose": otp.purpose,
        },
    )
    return otp, code


async def verify(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    purpose: str,
    code: str,
) -> OTP:
    """Consume the most-recent unconsumed OTP for user+purpose.

    Only the newest active OTP is considered — earlier issued-but-unconsumed
    codes for the same user+purpose are logically superseded by any subsequent
    `issue()` call (they still exist for audit but no longer verify).
    """
    user = await session.get(User, user_id)
    if user is None:
        raise UnknownUser()

    otp = (
        await session.execute(
            select(OTP)
            .where(
                OTP.user_id == user_id,
                OTP.purpose == purpose,
                OTP.consumed_at.is_(None),
            )
            .order_by(OTP.issued_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if otp is None:
        await _write_failed(
            session, user_id=user_id, otp_id=None, reason="no_active_code"
        )
        raise OTPVerificationFailed("no_active_code")

    now = _now()
    if otp.expires_at <= now:
        await _write_failed(
            session, user_id=user_id, otp_id=otp.id, reason="expired"
        )
        raise OTPVerificationFailed("expired")

    if not hmac.compare_digest(otp.code_hash, _hash_code(code)):
        await _write_failed(
            session, user_id=user_id, otp_id=otp.id, reason="wrong_code"
        )
        raise OTPVerificationFailed("wrong_code")

    otp.consumed_at = now
    await session.flush()

    await audit.append(
        session,
        actor_type="user",
        actor_id=str(user_id),
        event_name="otp.verified",
        subject_type="user",
        subject_id=str(user_id),
        payload={"user_id": str(user_id), "otp_id": str(otp.id), "purpose": purpose},
    )
    return otp


async def _write_failed(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    otp_id: uuid.UUID | None,
    reason: str,
) -> None:
    await audit.append(
        session,
        actor_type="user",
        actor_id=str(user_id),
        event_name="otp.verification_failed",
        subject_type="user",
        subject_id=str(user_id),
        payload={
            "user_id": str(user_id),
            "otp_id": str(otp_id) if otp_id is not None else None,
            "reason": reason,
        },
    )


async def user_has_verified_otp(
    session: AsyncSession, *, user_id: uuid.UUID, purpose: str
) -> bool:
    """Precondition check used by password-set (§4.1)."""
    match = (
        await session.execute(
            select(OTP.id).where(
                OTP.user_id == user_id,
                OTP.purpose == purpose,
                OTP.consumed_at.is_not(None),
            )
        )
    ).first()
    return match is not None
