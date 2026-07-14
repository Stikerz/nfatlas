"""One-shot superadmin bootstrap (ADR-009 §Bootstrapping).

Creates the first operator account so the wf-08 admin login has someone
to sign in as. Idempotent: if a user with ATLAS_SUPERADMIN_EMAIL already
exists, the script fixes up the password_hash + status + role grant and
exits 0. Safe to re-run.

Usage (from repo root):

    docker compose run --rm backend \
        python -m atlas.infrastructure.bootstrap_superadmin

Requires env vars (set in docker-compose or .env):
    ATLAS_SUPERADMIN_EMAIL
    ATLAS_SUPERADMIN_PASSWORD  (>= 12 chars, entropy your call)

The seed operator's Nigerian name (per wf-08 §1.4) is a display concern —
bootstrap uses whatever local-part the email has; the /admin TopBar
derives a display name from that.

This script INSERTS an audit-log row event_name='admin.bootstrapped' so
the chain records the moment of first-operator creation.
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from atlas.admin import service as admin_service
from atlas.audit_log import writer as audit
from atlas.config import get_settings
from atlas.identity.models import User
from atlas.identity.password_service import hash_password


async def _bootstrap(email: str, password: str) -> None:
    engine = create_async_engine(get_settings().database_url.get_secret_value())
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:  # type: AsyncSession
        existing = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()

        if existing is not None:
            user_id = existing.id
            existing.password_hash = hash_password(password)
            existing.status = "active"
            action = "updated"
        else:
            user = User(
                email=email,
                phone_e164="+2348030000000",  # placeholder; superadmin doesn't need SMS
                password_hash=hash_password(password),
                date_of_birth=date(1990, 1, 1),  # placeholder DOB satisfies 18+ check
                status="active",
            )
            session.add(user)
            await session.flush()
            user_id = user.id
            action = "created"

        await admin_service.grant_role(
            session, user_id=user_id, role_code=admin_service.SUPERADMIN_ROLE
        )

        await audit.append(
            session,
            actor_type="system",
            actor_id="bootstrap",
            event_name="admin.bootstrapped",
            subject_type="user",
            subject_id=str(user_id),
            payload={"user_id": str(user_id), "email": email, "action": action},
        )
        await session.commit()

        print(  # noqa: T201 — CLI output is the point
            f"→ {action} superadmin  id={user_id}  email={email}"
        )

    await engine.dispose()


def main() -> None:
    email = os.environ.get("ATLAS_SUPERADMIN_EMAIL")
    password = os.environ.get("ATLAS_SUPERADMIN_PASSWORD")
    if not email or not password:
        sys.stderr.write(
            "error: ATLAS_SUPERADMIN_EMAIL and ATLAS_SUPERADMIN_PASSWORD must be set.\n"
        )
        sys.exit(2)
    if len(password) < 12:
        sys.stderr.write("error: password must be at least 12 characters.\n")
        sys.exit(2)
    try:
        uuid.UUID  # noqa: B018 — imported for API surface stability
        asyncio.run(_bootstrap(email, password))
    except Exception as exc:  # noqa: BLE001 — CLI wrapper prints then exits
        sys.stderr.write(f"error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
