"""GET /api/v1/draws and GET /api/v1/draws/{id} — integration tests."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.draw.models import Draw


async def _seed_draw(
    session: AsyncSession,
    *,
    state: str = "sales_open",
    prize: str = "Win ₦2M",
) -> Draw:
    now = datetime.now(UTC)
    server_seed = b"test-seed-" + uuid.uuid4().bytes
    draw_id = uuid.uuid4()
    commitment = hashlib.sha256(server_seed + draw_id.bytes).hexdigest()
    row = Draw(
        id=draw_id,
        prize_copy=prize,
        ticket_price_minor=500_00,
        currency="NGN",
        close_time=now + timedelta(days=3),
        draw_time=now + timedelta(days=3, hours=1),
        state=state,
        commitment=commitment,
        server_seed_encrypted=server_seed.hex(),
    )
    session.add(row)
    await session.flush()
    return row


class TestListDraws:
    async def test_returns_only_sales_open(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        open_draw = await _seed_draw(db_session, state="sales_open")
        await _seed_draw(db_session, state="draft")
        await db_session.commit()

        response = await client.get("/api/v1/draws")
        assert response.status_code == 200
        items = response.json()["items"]
        ids = [i["id"] for i in items]
        assert str(open_draw.id) in ids
        for item in items:
            assert item["state"] == "sales_open"

    async def test_empty_list_when_no_active(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/draws")
        assert response.status_code == 200
        assert response.json() == {"items": []}


class TestGetDraw:
    async def test_returns_full_shape_including_commitment(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        draw = await _seed_draw(db_session)
        await db_session.commit()

        response = await client.get(f"/api/v1/draws/{draw.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == str(draw.id)
        assert body["prize_copy"] == draw.prize_copy
        assert body["ticket_price_minor"] == 500_00
        assert body["currency"] == "NGN"
        assert body["state"] == "sales_open"
        assert body["commitment"] == draw.commitment
        assert len(body["commitment"]) == 64  # sha256 hex

    async def test_unknown_returns_404(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/draws/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "draw_not_found"

    async def test_bad_uuid_returns_422(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/draws/not-a-uuid")
        assert response.status_code == 422


class TestServiceLayer:
    """Direct service tests — no HTTP roundtrip."""

    async def test_is_sales_open_true_for_open(
        self, db_session: AsyncSession
    ) -> None:
        from atlas.draw import service as draw_service

        draw = await _seed_draw(db_session, state="sales_open")
        await db_session.commit()
        assert await draw_service.is_sales_open(db_session, draw_id=draw.id) is True

    async def test_is_sales_open_false_for_other_states(
        self, db_session: AsyncSession
    ) -> None:
        from atlas.draw import service as draw_service

        for state in ("draft", "committed", "sales_closed", "revealed"):
            draw = await _seed_draw(db_session, state=state)
            await db_session.commit()
            assert (
                await draw_service.is_sales_open(db_session, draw_id=draw.id) is False
            )

    async def test_is_sales_open_false_for_unknown(
        self, db_session: AsyncSession
    ) -> None:
        from atlas.draw import service as draw_service

        assert (
            await draw_service.is_sales_open(db_session, draw_id=uuid.uuid4()) is False
        )
