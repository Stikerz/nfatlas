"""Test fixtures — real Postgres, no mocks (per AINE-AGENTS.md §8.6).

Day 1: minimal — smoke test that the app boots and /healthz responds.
Day 2 expands with `db_session`, per-test truncation of identity tables,
and helpers for asserting audit-log chain integrity.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from atlas.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
