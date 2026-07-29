"""Demo-day close + reveal helper.

Drives the seeded draw (DEMO_DRAW_ID from seed_v0_5.py) through
close → reveal in one command so the founder's demo pitch doesn't
need two curl calls with an idempotency-key each. Prints the winner
ticket + the proof-endpoint URL for follow-on `verify_draw.py`
invocation.

Usage (from repo root):

    docker compose run --rm backend \\
        python /infrastructure/scripts/demo_close_reveal.py

Requires seed_v0_5.py to have run (so DEMO_DRAW_ID exists in
'sales_open' state).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "backend" / "src"))

from atlas.db import get_sessionmaker  # noqa: E402
from atlas.draw import service as draw_service  # noqa: E402
from infrastructure.scripts.seed_v0_5 import DEMO_DRAW_ID  # type: ignore[import-not-found]  # noqa: E402


async def _main_async() -> None:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        try:
            await draw_service.close_draw(session, draw_id=DEMO_DRAW_ID)
        except draw_service.DrawStateError:
            # Already closed — proceed to reveal.
            pass
        draw = await draw_service.reveal_draw(session, draw_id=DEMO_DRAW_ID)
        winners = await draw_service.list_winners(session, draw_id=DEMO_DRAW_ID)
        await session.commit()

    primary = winners[0] if winners else None
    sys.stdout.write(
        f"demo draw {DEMO_DRAW_ID} → state={draw.state}\n"
        f"  tickets_hash: {draw.tickets_hash}\n"
        f"  commitment:   {draw.commitment}\n"
    )
    if primary is not None:
        sys.stdout.write(
            f"  primary winner: ticket={primary.ticket_id} user={primary.user_id}\n"
            f"  reserves:      {len(winners) - 1}\n"
        )
    sys.stdout.write(
        f"\nProof URL: http://localhost:8000/api/v1/draws/{DEMO_DRAW_ID}/proof\n"
        f"Verify:    python backend/tools/verify_draw.py "
        f"--proof-url http://localhost:8000/api/v1/draws/{DEMO_DRAW_ID}/proof\n"
    )


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
