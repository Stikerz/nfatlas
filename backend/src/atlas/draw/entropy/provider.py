"""Composite entropy provider — bundles bitcoin + drand for one fetch.

The reveal handler calls `default_provider().fetch(close_time)` and
gets back `EntropyInputs` with both primitives populated + a
`verified_at` timestamp.

Mode selection is driven by `Settings.draw_entropy_mode`. Stub
selection is the default for tests + CI; live selection requires a
`ATLAS_DRAW_ENTROPY_MODE=live` explicit set.
"""

from __future__ import annotations

from datetime import UTC, datetime

from atlas.config import get_settings
from atlas.draw.entropy import bitcoin, drand
from atlas.draw.entropy.protocol import EntropyInputs, EntropyProvider


class CompositeEntropyProvider:
    """Implements `EntropyProvider`. Mode chosen at construction time
    from config; each fetch stays in that mode."""

    def __init__(self, *, mode: str | None = None) -> None:
        self.mode = mode or get_settings().draw_entropy_mode

    async def fetch(self, close_time: datetime) -> EntropyInputs:
        if self.mode == "live":
            bitcoin_entropy = await bitcoin.fetch_live(close_time)
            drand_entropy = await drand.fetch_live(close_time)
        else:
            bitcoin_entropy = await bitcoin.fetch_stub(close_time)
            drand_entropy = await drand.fetch_stub(close_time)

        return EntropyInputs(
            bitcoin=bitcoin_entropy,
            drand=drand_entropy,
            verified_at=datetime.now(UTC),
            mode=self.mode,
        )


def default_provider() -> EntropyProvider:
    return CompositeEntropyProvider()
