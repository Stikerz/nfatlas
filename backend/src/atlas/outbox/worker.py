"""Outbox worker — polls, dispatches, retries, dead-letters (ADR-002).

Entry point: `python -m atlas.outbox.worker`. Compose runs this in the
`worker` service; the same Docker image serves the API.

Design contract:
  - `run_once(session, batch_size, max_attempts)` — one polling cycle.
    Locks up to `batch_size` due rows via `FOR UPDATE SKIP LOCKED`,
    dispatches each, marks processed / retries with exponential backoff /
    moves to `outbox_dead_letter` after `max_attempts`. Commits at the
    end. Safe to run concurrently with other workers.
  - `run_forever(sessionmaker)` — 1-second poll floor per ADR-002.

Consumer contract: handlers see at-least-once delivery. A worker crash
between dispatch and commit releases row locks; another worker (or a
subsequent poll) picks the row up again. Handlers must be idempotent.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from atlas.config import get_settings
from atlas.outbox.dispatcher import HANDLERS
from atlas.outbox.models import OutboxDeadLetterRow, OutboxRow

logger = logging.getLogger("atlas.outbox.worker")


def _backoff(attempts: int) -> timedelta:
    """min(60s * 2^attempts, 1h) per ADR-002 §Processing model."""
    seconds = min(60 * (2 ** attempts), 3600)
    return timedelta(seconds=seconds)


async def _move_to_dead_letter(session: AsyncSession, row: OutboxRow) -> None:
    session.add(
        OutboxDeadLetterRow(
            original_id=row.id,
            event_name=row.event_name,
            aggregate_type=row.aggregate_type,
            aggregate_id=row.aggregate_id,
            payload=row.payload,
            correlation_id=row.correlation_id,
            created_at=row.created_at,
            attempts=row.attempts,
            last_error=row.last_error,
        )
    )
    await session.delete(row)


async def run_once(
    session: AsyncSession, *, batch_size: int, max_attempts: int
) -> int:
    """Dispatch one batch. Returns count of rows locked (successes + failures)."""
    now = datetime.now(UTC)
    rows = (
        await session.execute(
            select(OutboxRow)
            .where(
                OutboxRow.processed_at.is_(None),
                OutboxRow.next_attempt_at <= now,
            )
            .order_by(OutboxRow.id)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
    ).scalars().all()

    for row in rows:
        handler = HANDLERS.get(row.event_name)
        if handler is None:
            row.attempts += 1
            row.last_error = f"no handler registered for {row.event_name!r}"
            logger.error(
                "outbox: no handler for event=%s id=%s — dead-lettering",
                row.event_name,
                row.id,
            )
            await _move_to_dead_letter(session, row)
            continue
        try:
            await handler(session, row.payload)
        except Exception as exc:
            row.attempts += 1
            row.last_error = str(exc)[:1024]
            if row.attempts >= max_attempts:
                logger.error(
                    "outbox: dispatch failed permanently event=%s id=%s "
                    "attempts=%d — dead-lettering",
                    row.event_name,
                    row.id,
                    row.attempts,
                )
                await _move_to_dead_letter(session, row)
            else:
                row.next_attempt_at = datetime.now(UTC) + _backoff(row.attempts)
                logger.warning(
                    "outbox: dispatch failed event=%s id=%s attempts=%d "
                    "next_attempt_at=%s",
                    row.event_name,
                    row.id,
                    row.attempts,
                    row.next_attempt_at.isoformat(),
                )
        else:
            row.processed_at = datetime.now(UTC)

    await session.commit()
    return len(rows)


# Touched after every completed poll cycle. The container healthcheck reads its
# mtime, so a wedged or crash-looping loop stops looking healthy — the previous
# check only asserted that the interpreter starts, which it does either way.
HEARTBEAT_PATH = Path("/tmp/atlas-outbox-worker.heartbeat")


def _beat() -> None:
    """Record that a poll cycle completed. Never fatal: a worker that cannot
    write its heartbeat should keep dispatching, not die."""
    try:
        HEARTBEAT_PATH.write_text(str(time.time()))
    except OSError:
        logger.warning("outbox worker: could not write heartbeat", exc_info=True)


async def run_forever(sessionmaker: async_sessionmaker[AsyncSession]) -> None:
    """Poll loop with 1-second floor per ADR-002 §Trade-offs."""
    settings = get_settings()
    poll_interval = settings.outbox_poll_interval_seconds
    batch_size = settings.outbox_batch_size
    max_attempts = settings.outbox_max_attempts

    logger.info(
        "outbox worker starting: poll=%ss batch=%d max_attempts=%d",
        poll_interval,
        batch_size,
        max_attempts,
    )
    while True:
        try:
            async with sessionmaker() as session:
                await run_once(
                    session, batch_size=batch_size, max_attempts=max_attempts
                )
            # Only after a clean cycle: a loop that throws every time must not
            # keep reporting itself alive.
            _beat()
        except Exception:
            logger.exception("outbox worker cycle crashed; will retry after sleep")
        await asyncio.sleep(poll_interval)


def _main() -> None:
    """Entry point for `python -m atlas.outbox.worker`."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = get_settings()
    engine = create_async_engine(settings.database_url.get_secret_value())
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    asyncio.run(run_forever(sessionmaker))


if __name__ == "__main__":
    _main()
