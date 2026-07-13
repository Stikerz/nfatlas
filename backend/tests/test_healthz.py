"""Day 1 smoke: the app boots and /healthz returns 200."""

from __future__ import annotations

from httpx import AsyncClient


async def test_healthz_ok(client: AsyncClient) -> None:
    response = await client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
