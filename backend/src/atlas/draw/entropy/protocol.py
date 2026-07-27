"""Entropy provider protocol + return types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class BitcoinBlockEntropy:
    """Cross-verified across mempool.space + blockstream.info in live
    mode. Both explorers must return the same block hash for the given
    close_time."""

    block_height: int
    block_hash: str        # 32-byte SHA-256 double-hash, hex
    block_timestamp: int   # Unix epoch, seconds


@dataclass(frozen=True)
class DrandRoundEntropy:
    """The drand round whose epoch is the smallest ≥ close_time.

    `randomness` is the SHA-256 of the BLS signature — the value the
    Reserve algorithm consumes. BLS-signature verification against the
    League of Entropy group public key is a V1 hardening (see
    week-6-build-plan §6 risk 3); V0.5 trusts the drand HTTPS endpoint,
    which returns already-verified randomness server-side."""

    round: int
    randomness: str        # 32-byte, hex
    signature: str         # BLS signature bytes, hex — persisted for V1 verify


@dataclass(frozen=True)
class EntropyInputs:
    """Bundled reveal-time entropy — the payload the reveal handler
    hands to `select_winners` per ADR-006 §Reserve algorithm."""

    bitcoin: BitcoinBlockEntropy
    drand: DrandRoundEntropy
    verified_at: datetime  # UTC, when both were fetched + cross-checked
    mode: str              # 'stub' | 'live' — audit-trail hint

    @property
    def combined_bytes(self) -> bytes:
        """Concatenated bytes fed into `select_winners` — the ordering
        matters for reproducibility. Bitcoin first, then drand."""
        return bytes.fromhex(self.bitcoin.block_hash) + bytes.fromhex(
            self.drand.randomness
        )


class EntropyFetchError(RuntimeError):
    """A live-mode fetch failed after retries — network, 5xx, or
    signature-verification failure."""


class EntropyMismatchError(RuntimeError):
    """The two Bitcoin explorers returned different block hashes for
    the same close_time. Aborts reveal per ADR-006 §Protocol stage 4."""


class EntropyProvider(Protocol):
    """Adapter interface. Callers pass a close_time (UTC); the provider
    returns EntropyInputs or raises EntropyFetchError/Mismatch."""

    mode: str

    async def fetch(self, close_time: datetime) -> EntropyInputs: ...
