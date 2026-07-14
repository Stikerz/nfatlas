"""RBAC service helpers per ADR-009.

Callers outside atlas.admin should use these — reading user_roles directly
from another module is a boundary violation.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin.models import UserRole

SUPERADMIN_ROLE = "superadmin"
USER_ROLE = "user"


async def roles_for(session: AsyncSession, *, user_id: uuid.UUID) -> list[str]:
    """Return the role codes granted to a user, sorted for deterministic order."""
    rows = (
        await session.execute(
            select(UserRole.role_code).where(UserRole.user_id == user_id)
        )
    ).scalars().all()
    return sorted(set(rows))


async def is_superadmin(session: AsyncSession, *, user_id: uuid.UUID) -> bool:
    return SUPERADMIN_ROLE in await roles_for(session, user_id=user_id)


async def grant_role(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    role_code: str,
    granted_by: uuid.UUID | None = None,
) -> None:
    """Idempotent role grant. No-op if the row already exists."""
    existing = (
        await session.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_code == role_code,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return
    session.add(
        UserRole(user_id=user_id, role_code=role_code, granted_by=granted_by)
    )
    await session.flush()
