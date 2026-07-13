"""Password set + verify.

bcrypt cost 12 per week-3-build-plan §2 Day 3. Password set requires a prior
consumed OTP with purpose='registration' for the user (plan §5 test list).
"""

from __future__ import annotations

import uuid

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.identity import otp_service
from atlas.identity.models import User

BCRYPT_COST = 12


class OTPPrerequisiteMissing(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "otp_prerequisite_missing",
                "message": "Verify a registration OTP before setting a password.",
            },
        )


class InvalidCredentials(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "invalid_credentials",
                "message": "Email or password is incorrect.",
            },
        )


def hash_password(plaintext: str) -> str:
    return bcrypt.hashpw(
        plaintext.encode("utf-8"),
        bcrypt.gensalt(rounds=BCRYPT_COST),
    ).decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


async def set_password(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    plaintext: str,
) -> None:
    user = await session.get(User, user_id)
    if user is None:
        raise otp_service.UnknownUser()

    if not await otp_service.user_has_verified_otp(
        session, user_id=user_id, purpose="registration"
    ):
        raise OTPPrerequisiteMissing()

    user.password_hash = hash_password(plaintext)
    user.status = "active"
    await session.flush()

    await audit.append(
        session,
        actor_type="user",
        actor_id=str(user_id),
        event_name="user.password_set",
        subject_type="user",
        subject_id=str(user_id),
        payload={"user_id": str(user_id)},
    )
