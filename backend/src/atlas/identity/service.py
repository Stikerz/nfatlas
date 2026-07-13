"""Identity module service layer.

The only entrypoint by which other modules interact with identity state.
Direct SQL against users/otps/sessions from outside `atlas.identity` is
grep-forbidden in CI.
"""

from __future__ import annotations

import hashlib
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log import writer as audit
from atlas.identity.models import User
from atlas.identity.schemas import RegisterRequest, RegisterResponse

MIN_AGE_YEARS = 18


class ConflictError(HTTPException):
    def __init__(self, code: str, field: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": code, "field": field, "message": f"{field} already registered"},
        )


class UnderAgeError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "under_age",
                "message": "You must be 18 or over to register.",
            },
        )


def _is_18_or_over(dob: date, today: date) -> bool:
    years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return years >= MIN_AGE_YEARS


def _email_hash(email: str) -> str:
    """SHA-256 of the lowercased email for audit-log redaction (ADR-005 payload)."""
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()


async def register(session: AsyncSession, body: RegisterRequest) -> RegisterResponse:
    if not _is_18_or_over(body.date_of_birth, date.today()):
        raise UnderAgeError()

    user = User(
        email=str(body.email),
        phone_e164=body.phone_e164,
        date_of_birth=body.date_of_birth,
        status="pending_verification",
    )
    session.add(user)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        message = str(exc.orig).lower()
        if "email" in message:
            raise ConflictError("email_taken", "email") from exc
        if "phone" in message:
            raise ConflictError("phone_taken", "phone_e164") from exc
        raise

    await audit.append(
        session,
        actor_type="user",
        actor_id=str(user.id),
        event_name="user.registered",
        subject_type="user",
        subject_id=str(user.id),
        payload={
            "user_id": str(user.id),
            "email_hash": _email_hash(str(body.email)),
            "phone_e164": body.phone_e164,
            "dob_year": body.date_of_birth.year,
            "terms_accepted": True,
        },
    )
    return RegisterResponse(user_id=user.id, status=user.status)
