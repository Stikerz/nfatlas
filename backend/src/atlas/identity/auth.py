"""Authentication dependencies.

`current_session` decodes the Authorization: Bearer <jwt> header, verifies
signature + expiry + issuer, then loads the sessions row to enforce
revocation. Returns the ORM Session; the caller can read user_id from it.

Cross-module usage: any endpoint outside atlas.identity that needs the
logged-in user imports this dependency (a controlled cross-module import,
noted as expected in week-3-build-plan §6 handoff to Winston).
"""

from __future__ import annotations

import uuid

from fastapi import Depends, Header
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.db import get_session
from atlas.identity import session_service
from atlas.identity.models import Session


async def current_session(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_session),
) -> Session:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise session_service.SessionInvalid()

    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = session_service.decode_jwt(token)
    except InvalidTokenError as exc:
        raise session_service.SessionInvalid() from exc

    try:
        session_id = uuid.UUID(str(claims["jti"]))
    except (KeyError, ValueError) as exc:
        raise session_service.SessionInvalid() from exc

    return await session_service.load_active(db, session_id=session_id)
