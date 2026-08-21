"""Outbox writer — same-transaction semantics (ADR-002 §Idempotency)."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.events import WINNER_SELECTED_V1, WinnerSelectedPayload
from atlas.outbox import writer as outbox
from atlas.outbox.models import OutboxRow


def _sample_payload(**overrides: object) -> dict[str, object]:
    base = {
        "draw_id": str(uuid.uuid4()),
        "winner_id": str(uuid.uuid4()),
        "ticket_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "position": 0,
        "is_primary": True,
        "prize_copy": "Test prize",
    }
    base.update(overrides)
    return base


class TestEmitPersistence:
    async def test_emit_persists_after_commit(
        self, db_session: AsyncSession
    ) -> None:
        payload = _sample_payload()
        await outbox.emit(
            db_session,
            event_name=WINNER_SELECTED_V1,
            aggregate_type="draw_winner",
            aggregate_id=payload["winner_id"],
            payload=payload,
        )
        await db_session.commit()

        rows = (
            await db_session.execute(
                select(OutboxRow).where(OutboxRow.event_name == WINNER_SELECTED_V1)
            )
        ).scalars().all()
        assert len(rows) == 1
        row = rows[0]
        assert row.aggregate_id == payload["winner_id"]
        assert row.payload["draw_id"] == payload["draw_id"]
        assert row.processed_at is None
        assert row.attempts == 0
        assert row.next_attempt_at is not None

    async def test_emit_rolled_back_not_persisted(
        self, db_session: AsyncSession
    ) -> None:
        payload = _sample_payload()
        await outbox.emit(
            db_session,
            event_name=WINNER_SELECTED_V1,
            aggregate_type="draw_winner",
            aggregate_id=payload["winner_id"],
            payload=payload,
        )
        await db_session.rollback()

        rows = (
            await db_session.execute(
                select(OutboxRow).where(OutboxRow.event_name == WINNER_SELECTED_V1)
            )
        ).scalars().all()
        assert rows == []

    async def test_two_emits_in_one_transaction(
        self, db_session: AsyncSession
    ) -> None:
        draw_id = str(uuid.uuid4())
        for position in (0, 1):
            payload = _sample_payload(
                draw_id=draw_id, position=position, is_primary=(position == 0)
            )
            await outbox.emit(
                db_session,
                event_name=WINNER_SELECTED_V1,
                aggregate_type="draw_winner",
                aggregate_id=payload["winner_id"],
                payload=payload,
            )
        await db_session.commit()

        rows = (
            await db_session.execute(
                select(OutboxRow).where(
                    OutboxRow.payload["draw_id"].astext == draw_id
                )
            )
        ).scalars().all()
        assert len(rows) == 2


class TestPayloadValidation:
    async def test_missing_required_field_rejected(
        self, db_session: AsyncSession
    ) -> None:
        payload = _sample_payload()
        del payload["draw_id"]  # required by WinnerSelectedPayload
        with pytest.raises(ValueError, match="draw_id"):
            await outbox.emit(
                db_session,
                event_name=WINNER_SELECTED_V1,
                aggregate_type="draw_winner",
                aggregate_id=payload["winner_id"],
                payload=payload,
            )

    async def test_unknown_event_name_rejected(
        self, db_session: AsyncSession
    ) -> None:
        with pytest.raises(ValueError, match="unknown event_name"):
            await outbox.emit(
                db_session,
                event_name="not.a.real.event.v1",
                aggregate_type="draw_winner",
                aggregate_id=str(uuid.uuid4()),
                payload=_sample_payload(),
            )


class TestPydanticSchema:
    def test_winner_selected_payload_round_trips(self) -> None:
        raw = {
            "draw_id": str(uuid.uuid4()),
            "winner_id": str(uuid.uuid4()),
            "ticket_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "position": 1,
            "is_primary": False,
            "prize_copy": "Reserve prize",
        }
        parsed = WinnerSelectedPayload.model_validate(raw)
        assert parsed.model_dump(mode="json") == raw


class TestPartialIndex:
    async def test_unprocessed_index_exists(
        self, db_session: AsyncSession
    ) -> None:
        result = (
            await db_session.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE tablename = 'outbox' AND indexname = "
                    "'outbox_unprocessed_idx'"
                )
            )
        ).scalar_one_or_none()
        assert result == "outbox_unprocessed_idx"
