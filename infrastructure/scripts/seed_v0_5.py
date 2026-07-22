"""V0.5 demo seed data — idempotent (safe to re-run).

Populated per week-5-build-plan §Day 1. Creates:
  - One `sales_open` draw with well-known ID (V0.5 shows exactly one
    active draw at a time). Prize copy, close_time = now+3d, draw_time
    = now+3d+1h, ticket_price = ₦500.
  - Server seed + commitment per ADR-006 §Protocol stage 1.
    TODO(week-6): encrypt server_seed at rest. V0.5 stores plaintext
    per week-5-build-plan §0 ask 5.
  - A pool of 10 skill questions with 3 or 4 options each.

Usage (from repo root, backend env loaded):

    docker compose run --rm backend \\
        python /infrastructure/scripts/seed_v0_5.py

Or locally in an activated venv:

    ATLAS_DATABASE_URL=... python infrastructure/scripts/seed_v0_5.py

Idempotent: uses UPSERT on well-known IDs so re-running the script
resets the demo state without drift. Existing tickets / attempts /
audit rows are NOT wiped — use `make demo-reset` (Week 7) for that.
"""

from __future__ import annotations

import asyncio
import hashlib
import secrets
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Path munge so the script works without the package being pip-installed
# (fresh clone / no venv activated).
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "backend" / "src"))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.dialects.postgresql import insert as pg_insert  # noqa: E402

from atlas.db import get_sessionmaker  # noqa: E402
from atlas.draw.models import Draw  # noqa: E402
from atlas.skill.models import SkillQuestion, SkillQuestionOption  # noqa: E402


# Well-known IDs — never change these; the demo state depends on them.
DEMO_DRAW_ID = uuid.UUID("01919abc-0d6a-7000-8000-000000000001")

# 10 questions — trivia + light general-knowledge. Chosen to be answerable
# without regional context so the demo works for any investor audience.
DEMO_QUESTIONS: list[tuple[uuid.UUID, str, list[tuple[str, bool]]]] = [
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000101"),
        "What is the capital of Nigeria?",
        [("Lagos", False), ("Abuja", True), ("Kano", False), ("Port Harcourt", False)],
    ),
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000102"),
        "Which colour is on the top stripe of the Nigerian flag?",
        [("Green", True), ("White", False), ("Red", False)],
    ),
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000103"),
        "How many minutes are there in an hour?",
        [("60", True), ("100", False), ("50", False)],
    ),
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000104"),
        "What is 12 multiplied by 12?",
        [("144", True), ("124", False), ("164", False), ("120", False)],
    ),
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000105"),
        "Which planet is known as the Red Planet?",
        [("Venus", False), ("Mars", True), ("Jupiter", False), ("Saturn", False)],
    ),
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000106"),
        "Water freezes at what temperature in Celsius?",
        [("0", True), ("32", False), ("100", False)],
    ),
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000107"),
        "How many continents are there on Earth?",
        [("5", False), ("6", False), ("7", True), ("8", False)],
    ),
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000108"),
        "What language has the most native speakers worldwide?",
        [("English", False), ("Mandarin Chinese", True), ("Spanish", False)],
    ),
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000109"),
        "Which currency is used in the United Kingdom?",
        [("Euro", False), ("Pound Sterling", True), ("Dollar", False)],
    ),
    (
        uuid.UUID("01919abc-0d6a-7000-8000-000000000110"),
        "What is the square root of 81?",
        [("7", False), ("8", False), ("9", True), ("10", False)],
    ),
]


def _commitment(server_seed: bytes, draw_id: uuid.UUID) -> str:
    """SHA-256(server_seed || draw_id_bytes) per ADR-006 §Protocol stage 1."""
    return hashlib.sha256(server_seed + draw_id.bytes).hexdigest()


async def _seed_draw(session) -> Draw:
    """Idempotent upsert of the demo draw."""
    now = datetime.now(UTC)
    close_time = now + timedelta(days=3)
    draw_time = close_time + timedelta(hours=1)

    # Deterministic server_seed per DEMO_DRAW_ID so the commitment stays
    # stable across re-seeds (a real reveal would rotate this per draw).
    # Real reveals happen Week 6 — for V0.5 the seed is a placeholder.
    # TODO(week-6): generate `secrets.token_bytes(32)` + encrypt-at-rest.
    server_seed = hashlib.sha256(b"atlas-v0.5-demo-seed:" + DEMO_DRAW_ID.bytes).digest()
    commitment = _commitment(server_seed, DEMO_DRAW_ID)

    values = {
        "id": DEMO_DRAW_ID,
        "prize_copy": "Win ₦2,000,000 cash or a mortgage-free Lagos apartment.",
        "ticket_price_minor": 500_00,  # ₦500
        "currency": "NGN",
        "close_time": close_time,
        "draw_time": draw_time,
        "state": "sales_open",
        "commitment": commitment,
        # TODO(week-6): encrypt with the platform secret manager.
        "server_seed_encrypted": server_seed.hex(),
    }
    stmt = (
        pg_insert(Draw)
        .values(**values)
        .on_conflict_do_update(
            index_elements=[Draw.id],
            set_={
                # Rotate the mutable demo attributes on re-seed; keep the
                # commitment stable so any tickets already minted still
                # reference a valid draw.
                "prize_copy": values["prize_copy"],
                "close_time": values["close_time"],
                "draw_time": values["draw_time"],
                "state": values["state"],
                "updated_at": now,
            },
        )
    )
    await session.execute(stmt)
    return await session.get(Draw, DEMO_DRAW_ID)


async def _seed_questions(session) -> int:
    """Idempotent upsert of the 10 demo skill questions + options."""
    for q_id, prompt, options in DEMO_QUESTIONS:
        q_stmt = (
            pg_insert(SkillQuestion)
            .values(id=q_id, prompt=prompt, active=True)
            .on_conflict_do_update(
                index_elements=[SkillQuestion.id],
                set_={"prompt": prompt, "active": True},
            )
        )
        await session.execute(q_stmt)

        # Options are deleted+reinserted on re-seed — simplest correct
        # behaviour given no FK from downstream data touches them yet.
        from sqlalchemy import delete

        await session.execute(
            delete(SkillQuestionOption).where(SkillQuestionOption.question_id == q_id)
        )
        for order, (text, is_correct) in enumerate(options):
            await session.execute(
                pg_insert(SkillQuestionOption).values(
                    question_id=q_id,
                    option_text=text,
                    is_correct=is_correct,
                    display_order=order,
                )
            )
    return len(DEMO_QUESTIONS)


async def _main_async() -> None:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        draw = await _seed_draw(session)
        question_count = await _seed_questions(session)
        await session.commit()

    sys.stdout.write(
        f"seeded draw {draw.id}\n"
        f"  prize: {draw.prize_copy}\n"
        f"  ticket_price: ₦{draw.ticket_price_minor / 100:,.2f}\n"
        f"  state: {draw.state}\n"
        f"  commitment: {draw.commitment}\n"
        f"seeded {question_count} skill questions\n"
    )


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
