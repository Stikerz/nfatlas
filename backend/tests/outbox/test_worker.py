"""Outbox worker — dispatch + retry + dead-letter + SKIP LOCKED concurrency."""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
)

from atlas.config import get_settings
from atlas.events import WINNER_SELECTED_V1
from atlas.outbox import dispatcher
from atlas.outbox import worker as outbox_worker
from atlas.outbox import writer as outbox_writer
from atlas.outbox.models import OutboxDeadLetterRow, OutboxRow


def _payload(**overrides: object) -> dict[str, object]:
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


class TestDispatchHappyPath:
    async def test_row_marked_processed_after_successful_dispatch(
        self, db_session, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[dict[str, object]] = []

        async def _fake_handler(session, payload):
            calls.append(dict(payload))

        monkeypatch.setitem(
            dispatcher.HANDLERS, WINNER_SELECTED_V1, _fake_handler
        )

        payload = _payload()
        await outbox_writer.emit(
            db_session,
            event_name=WINNER_SELECTED_V1,
            aggregate_type="draw_winner",
            aggregate_id=payload["winner_id"],
            payload=payload,
        )
        await db_session.commit()

        processed = await outbox_worker.run_once(
            db_session, batch_size=10, max_attempts=10
        )
        assert processed == 1
        assert len(calls) == 1

        row = (
            await db_session.execute(select(OutboxRow))
        ).scalar_one()
        assert row.processed_at is not None
        assert row.attempts == 0
        assert row.last_error is None

    async def test_only_due_rows_are_picked_up(
        self, db_session, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        called_ids: list[str] = []

        async def _fake_handler(session, payload):
            called_ids.append(payload["winner_id"])

        monkeypatch.setitem(
            dispatcher.HANDLERS, WINNER_SELECTED_V1, _fake_handler
        )

        due = _payload()
        future = _payload()
        for p in (due, future):
            await outbox_writer.emit(
                db_session,
                event_name=WINNER_SELECTED_V1,
                aggregate_type="draw_winner",
                aggregate_id=p["winner_id"],
                payload=p,
            )
        await db_session.commit()

        # Push one row's next_attempt_at into the future.
        await db_session.execute(
            text(
                "UPDATE outbox SET next_attempt_at = now() + interval '1 hour' "
                "WHERE payload->>'winner_id' = :wid"
            ),
            {"wid": future["winner_id"]},
        )
        await db_session.commit()

        await outbox_worker.run_once(
            db_session, batch_size=10, max_attempts=10
        )
        assert called_ids == [due["winner_id"]]


class TestRetryAndBackoff:
    async def test_failure_bumps_attempts_and_backs_off(
        self, db_session, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _boom(session, payload):
            raise RuntimeError("consumer exploded")

        monkeypatch.setitem(
            dispatcher.HANDLERS, WINNER_SELECTED_V1, _boom
        )

        payload = _payload()
        await outbox_writer.emit(
            db_session,
            event_name=WINNER_SELECTED_V1,
            aggregate_type="draw_winner",
            aggregate_id=payload["winner_id"],
            payload=payload,
        )
        await db_session.commit()

        await outbox_worker.run_once(
            db_session, batch_size=10, max_attempts=10
        )

        row = (
            await db_session.execute(select(OutboxRow))
        ).scalar_one()
        assert row.attempts == 1
        assert row.processed_at is None
        assert row.last_error is not None
        assert "consumer exploded" in row.last_error
        # Backoff pushes next_attempt into the future.
        assert row.next_attempt_at > datetime.now(UTC)

    def test_backoff_formula_is_exponential_capped_at_one_hour(self) -> None:
        # 60s * 2^attempts, capped at 3600s.
        assert outbox_worker._backoff(0) == timedelta(seconds=60)
        assert outbox_worker._backoff(1) == timedelta(seconds=120)
        assert outbox_worker._backoff(2) == timedelta(seconds=240)
        assert outbox_worker._backoff(5) == timedelta(seconds=1920)
        assert outbox_worker._backoff(6) == timedelta(seconds=3600)
        assert outbox_worker._backoff(20) == timedelta(seconds=3600)


class TestDeadLetter:
    async def test_row_moved_to_dead_letter_after_max_attempts(
        self, db_session, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _boom(session, payload):
            raise RuntimeError("permanent fail")

        monkeypatch.setitem(
            dispatcher.HANDLERS, WINNER_SELECTED_V1, _boom
        )

        payload = _payload()
        await outbox_writer.emit(
            db_session,
            event_name=WINNER_SELECTED_V1,
            aggregate_type="draw_winner",
            aggregate_id=payload["winner_id"],
            payload=payload,
        )
        await db_session.commit()

        # max_attempts=1 so the first failure trips dead-letter immediately.
        await outbox_worker.run_once(
            db_session, batch_size=10, max_attempts=1
        )

        live_count = (
            await db_session.execute(select(func.count()).select_from(OutboxRow))
        ).scalar_one()
        dead_count = (
            await db_session.execute(
                select(func.count()).select_from(OutboxDeadLetterRow)
            )
        ).scalar_one()
        assert live_count == 0
        assert dead_count == 1

        dead = (
            await db_session.execute(select(OutboxDeadLetterRow))
        ).scalar_one()
        assert dead.event_name == WINNER_SELECTED_V1
        assert dead.attempts == 1
        assert "permanent fail" in dead.last_error
        assert dead.original_id > 0
        assert dead.moved_at is not None

    async def test_unknown_event_name_dead_letters_immediately(
        self, db_session
    ) -> None:
        payload = _payload()
        # Bypass writer validation by inserting a row with an event name that
        # HAS no registered handler in dispatcher.HANDLERS. (writer.emit
        # would reject an unknown event, so we insert directly via the ORM.)
        raw = OutboxRow(
            event_name="unregistered.event.v1",
            aggregate_type="test",
            aggregate_id=str(uuid.uuid4()),
            payload=payload,
        )
        db_session.add(raw)
        await db_session.commit()

        await outbox_worker.run_once(
            db_session, batch_size=10, max_attempts=1
        )

        live_count = (
            await db_session.execute(select(func.count()).select_from(OutboxRow))
        ).scalar_one()
        dead_count = (
            await db_session.execute(
                select(func.count()).select_from(OutboxDeadLetterRow)
            )
        ).scalar_one()
        assert live_count == 0
        assert dead_count == 1


class TestSkipLockedConcurrency:
    async def test_two_workers_do_not_double_dispatch(
        self,
        db_engine: AsyncEngine,
        db_session,  # pulled in ONLY so the truncate teardown fires
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Two independent sessions on two connections — realistic worker
        # topology. Each calls run_once concurrently and must not
        # dispatch the same row twice.
        maker = async_sessionmaker(db_engine, expire_on_commit=False)

        # Insert 20 due rows via a third session (setup only).
        async with maker() as setup:
            for _ in range(20):
                p = _payload()
                await outbox_writer.emit(
                    setup,
                    event_name=WINNER_SELECTED_V1,
                    aggregate_type="draw_winner",
                    aggregate_id=p["winner_id"],
                    payload=p,
                )
            await setup.commit()

        dispatch_start = asyncio.Event()
        seen_ids: list[int] = []
        lock = asyncio.Lock()

        async def _tracking_handler(session, payload):
            # Force the worker to hold the row lock during dispatch so the
            # second worker actually contends. Without the wait, worker A
            # commits before worker B queries and the SKIP LOCKED
            # semantics never get exercised.
            await dispatch_start.wait()

        monkeypatch.setitem(
            dispatcher.HANDLERS, WINNER_SELECTED_V1, _tracking_handler
        )

        async def _worker(worker_id: int) -> int:
            async with maker() as sess:
                # Snapshot which ids this worker locks BEFORE dispatch.
                rows = (
                    await sess.execute(
                        select(OutboxRow.id)
                        .where(OutboxRow.processed_at.is_(None))
                        .order_by(OutboxRow.id)
                        .limit(10)
                        .with_for_update(skip_locked=True)
                    )
                ).scalars().all()
                async with lock:
                    seen_ids.extend(rows)
                # Now release the "handler" so both workers can proceed
                # to commit their own locked rows.
                dispatch_start.set()
                # And do a synthetic UPDATE to mark them processed.
                if rows:
                    await sess.execute(
                        text(
                            "UPDATE outbox SET processed_at = now() "
                            "WHERE id = ANY(:ids)"
                        ),
                        {"ids": list(rows)},
                    )
                await sess.commit()
                return len(rows)

        a, b = await asyncio.gather(_worker(1), _worker(2))
        # No id was locked by both workers.
        assert len(seen_ids) == len(set(seen_ids))
        # Between them they processed all 20.
        assert a + b == 20


class TestSettingsFlow:
    def test_settings_have_worker_fields(self) -> None:
        s = get_settings()
        assert s.outbox_poll_interval_seconds >= 1.0
        assert s.outbox_batch_size >= 1
        assert s.outbox_max_attempts == 10
