"""atlas.draw.entropy — stub-mode determinism unit tests.

Stub mode is what tests + CI run under. Determinism per close_time is
load-bearing — the verifier CLI must reach the same winner on replay
against the same proof inputs.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from atlas.draw.entropy import bitcoin, drand
from atlas.draw.entropy.provider import CompositeEntropyProvider


class TestBitcoinStub:
    async def test_deterministic_same_close_time(self) -> None:
        t = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        first = await bitcoin.fetch_stub(t)
        second = await bitcoin.fetch_stub(t)
        assert first == second

    async def test_different_close_times_produce_different_hashes(self) -> None:
        t1 = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        t2 = datetime(2026, 8, 4, 12, 0, 1, tzinfo=UTC)
        assert (await bitcoin.fetch_stub(t1)).block_hash != (
            await bitcoin.fetch_stub(t2)
        ).block_hash

    async def test_block_hash_is_hex_sha256(self) -> None:
        t = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        result = await bitcoin.fetch_stub(t)
        assert len(result.block_hash) == 64
        assert int(result.block_hash, 16) >= 0


class TestDrandRoundDerivation:
    """Golden vectors for drand round math. Fixed inputs → fixed rounds."""

    def test_round_at_or_after_pre_genesis(self) -> None:
        # Well before genesis → round 1 (never round 0; drand's own semantic).
        t = datetime(2020, 1, 1, tzinfo=UTC)
        assert drand.round_at_or_after(t) == 1

    def test_round_at_genesis_plus_period_is_1(self) -> None:
        t = datetime.fromtimestamp(
            drand.DRAND_MAINNET_GENESIS + drand.DRAND_MAINNET_PERIOD_SECONDS,
            tz=UTC,
        )
        assert drand.round_at_or_after(t) == 1

    def test_round_ceiling(self) -> None:
        # exactly at (genesis + N * period) → round N.
        t = datetime.fromtimestamp(
            drand.DRAND_MAINNET_GENESIS + 100 * drand.DRAND_MAINNET_PERIOD_SECONDS,
            tz=UTC,
        )
        assert drand.round_at_or_after(t) == 100

    def test_round_ceiling_off_by_one(self) -> None:
        # Just past N*period → round N+1 (not N).
        t = datetime.fromtimestamp(
            drand.DRAND_MAINNET_GENESIS + 100 * drand.DRAND_MAINNET_PERIOD_SECONDS + 1,
            tz=UTC,
        )
        assert drand.round_at_or_after(t) == 101


class TestDrandStub:
    async def test_deterministic_same_close_time(self) -> None:
        t = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        first = await drand.fetch_stub(t)
        second = await drand.fetch_stub(t)
        assert first == second

    async def test_round_matches_derivation(self) -> None:
        t = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        result = await drand.fetch_stub(t)
        assert result.round == drand.round_at_or_after(t)


class TestCompositeProvider:
    async def test_stub_mode_returns_populated_inputs(self) -> None:
        provider = CompositeEntropyProvider(mode="stub")
        t = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        inputs = await provider.fetch(t)

        assert inputs.mode == "stub"
        assert len(inputs.bitcoin.block_hash) == 64
        assert inputs.drand.round >= 1
        assert inputs.verified_at.tzinfo is not None

    async def test_combined_bytes_stable_across_runs(self) -> None:
        provider = CompositeEntropyProvider(mode="stub")
        t = datetime(2026, 8, 4, 12, 0, 0, tzinfo=UTC)
        first = await provider.fetch(t)
        second = await provider.fetch(t)
        assert first.combined_bytes == second.combined_bytes
        # 32 bytes bitcoin + 32 bytes drand = 64.
        assert len(first.combined_bytes) == 64

    async def test_mode_selection_from_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        provider = CompositeEntropyProvider(mode="stub")
        assert provider.mode == "stub"

        provider_live = CompositeEntropyProvider(mode="live")
        assert provider_live.mode == "live"
