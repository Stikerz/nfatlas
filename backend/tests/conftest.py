"""Test fixtures — real Postgres, no mocks (per AINE-AGENTS.md §8.6).

The suite runs against the Postgres service defined in `docker-compose.yaml`
(or the CI `postgres` service). ATLAS_DATABASE_URL points at the same DB
that Alembic upgraded to head; per-test truncation resets state.

`alembic upgrade head` runs once via `pytest_sessionstart` — synchronous,
so no async fixture scoping games. Each test gets its own engine + session
(engine creation is cheap; the connection pool warms on first use).
"""

from __future__ import annotations

import subprocess
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from atlas.config import get_settings
from atlas.db import get_session
from atlas.main import app

_TRUNCATE_TABLES = (
    "audit_log",
    "idempotency_records",
    "ledger_entries",
    "payment_intents",
    "skill_question_attempts",
    "skill_question_options",
    "skill_questions",
    "draws",
    "sessions",
    "otps",
    "user_roles",
    "users",
)

# Rows added per-test into ledger_accounts (user_wallet, prize_pool) are wiped;
# the 4 operator-level singletons seeded by migration 0004 stay put.
_LEDGER_ACCOUNTS_KEEP_TYPES = (
    "operator_revenue",
    "refund_payable",
    "payment_gateway_clearing",
    "tax_payable",
)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Bring the DB to head once, before any tests run."""
    backend_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["alembic", "-c", "migrations/alembic.ini", "upgrade", "head"],
        cwd=backend_root,
        check=True,
    )


@pytest.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(get_settings().database_url.get_secret_value())
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with db_engine.begin() as conn:
        await conn.execute(
            text(
                f"TRUNCATE TABLE {', '.join(_TRUNCATE_TABLES)} "
                "RESTART IDENTITY CASCADE"
            )
        )
        keep = ", ".join(f"'{t}'" for t in _LEDGER_ACCOUNTS_KEEP_TYPES)
        await conn.execute(
            text(f"DELETE FROM ledger_accounts WHERE account_type NOT IN ({keep})")
        )


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def _override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
