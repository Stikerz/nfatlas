"""POST /api/v1/users — integration tests against real Postgres.

Covers the Day 2 register slice per week-3-build-plan.md §5.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.audit_log.models import AuditLog
from atlas.audit_log.writer import GENESIS_HASH
from atlas.identity.models import User


def _valid_body(
    *,
    email: str = "kemi.adigun@example.com",
    phone: str = "+2348030000000",
    dob: date | None = None,
    terms: bool = True,
) -> dict[str, object]:
    return {
        "email": email,
        "phone_e164": phone,
        "date_of_birth": (dob or date(1993, 3, 12)).isoformat(),
        "terms_accepted": terms,
    }


def _headers(key: str | None = None) -> dict[str, str]:
    return {"Idempotency-Key": key or str(uuid.uuid4())}


async def test_register_happy_path(client: AsyncClient, db_session: AsyncSession) -> None:
    response = await client.post("/api/v1/users", json=_valid_body(), headers=_headers())

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending_verification"
    uuid.UUID(body["user_id"])

    user_row = (await db_session.execute(select(User))).scalar_one()
    assert user_row.email == "kemi.adigun@example.com"
    assert user_row.status == "pending_verification"

    audit = (await db_session.execute(select(AuditLog).order_by(AuditLog.seq))).scalars().all()
    assert len(audit) == 1
    assert audit[0].event_name == "user.registered"
    assert audit[0].prev_hash == GENESIS_HASH
    assert audit[0].payload["dob_year"] == 1993
    assert "@" not in audit[0].payload["email_hash"]  # hashed, not raw


async def test_register_under_18_rejected(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    under_18 = date.today() - timedelta(days=17 * 365)
    response = await client.post(
        "/api/v1/users",
        json=_valid_body(dob=under_18),
        headers=_headers(),
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "under_age"

    user_count = (await db_session.execute(select(func.count()).select_from(User))).scalar_one()
    audit_count = (
        await db_session.execute(select(func.count()).select_from(AuditLog))
    ).scalar_one()
    assert user_count == 0
    assert audit_count == 0


async def test_register_duplicate_email_conflict(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await client.post("/api/v1/users", json=_valid_body(), headers=_headers())
    response = await client.post(
        "/api/v1/users",
        json=_valid_body(phone="+2348039999999"),
        headers=_headers(),
    )
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "email_taken"

    user_count = (await db_session.execute(select(func.count()).select_from(User))).scalar_one()
    assert user_count == 1


async def test_register_missing_idempotency_key_400(client: AsyncClient) -> None:
    response = await client.post("/api/v1/users", json=_valid_body())
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "idempotency_key_required"


async def test_register_reused_key_same_body_returns_original_response(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    key = str(uuid.uuid4())
    first = await client.post("/api/v1/users", json=_valid_body(), headers=_headers(key))
    second = await client.post("/api/v1/users", json=_valid_body(), headers=_headers(key))

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()

    user_count = (await db_session.execute(select(func.count()).select_from(User))).scalar_one()
    assert user_count == 1


async def test_register_reused_key_different_body_conflict(client: AsyncClient) -> None:
    key = str(uuid.uuid4())
    first = await client.post("/api/v1/users", json=_valid_body(), headers=_headers(key))
    second = await client.post(
        "/api/v1/users",
        json=_valid_body(email="different@example.com"),
        headers=_headers(key),
    )
    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "idempotency_key_conflict"


async def test_audit_log_chain_integrity_across_registrations(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    for i in range(3):
        response = await client.post(
            "/api/v1/users",
            json=_valid_body(
                email=f"user{i}@example.com",
                phone=f"+234803000000{i}",
            ),
            headers=_headers(),
        )
        assert response.status_code == 201, response.text

    audit = (await db_session.execute(select(AuditLog).order_by(AuditLog.seq))).scalars().all()
    assert len(audit) == 3
    assert audit[0].prev_hash == GENESIS_HASH
    assert audit[1].prev_hash == audit[0].row_hash
    assert audit[2].prev_hash == audit[1].row_hash


@pytest.mark.parametrize(
    "phone",
    ["1234", "+1234567890", "+2341030000000", "+234803123456789"],
)
async def test_register_rejects_non_nigerian_phone(client: AsyncClient, phone: str) -> None:
    response = await client.post(
        "/api/v1/users",
        json=_valid_body(phone=phone),
        headers=_headers(),
    )
    assert response.status_code == 422


async def test_register_rejects_terms_not_accepted(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/users",
        json=_valid_body(terms=False),
        headers=_headers(),
    )
    assert response.status_code == 422
