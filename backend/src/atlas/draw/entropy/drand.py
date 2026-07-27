"""drand League-of-Entropy randomness adapter (ADR-006 §Protocol stage 4).

Live mode fetches the drand round whose epoch is the smallest ≥
close_time from `https://api.drand.sh/public/{round}`. Stub mode
returns a deterministic SHA-256 of close_time.

drand mainnet chain (default chain):
  - Genesis time: 1595431050 (Unix seconds)
  - Period:       30 seconds
  - Public key:   see https://drand.love/developer/http-api/#chain-info
                  Persisted in config as ATLAS_DRAND_GROUP_PUBLIC_KEY
                  for the V1 client-side BLS verify.

BLS signature verification: drand's HTTPS endpoint returns already-
verified randomness — the server runs the BLS check before serving.
Client-side verify is defense-in-depth against a compromised HTTPS
endpoint. V1 hardening; V0.5 trusts the endpoint and persists the raw
signature for later replay-verify (see week-6-build-plan §6 risk 3).
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

import httpx

from atlas.draw.entropy.protocol import DrandRoundEntropy, EntropyFetchError

DRAND_API_BASE = "https://api.drand.sh"
DRAND_MAINNET_GENESIS = 1_595_431_050
DRAND_MAINNET_PERIOD_SECONDS = 30
_TIMEOUT = httpx.Timeout(5.0, connect=3.0)


def round_at_or_after(close_time: datetime) -> int:
    """Deterministic round derivation: the smallest round whose epoch
    (genesis + round * period) is ≥ close_time. Golden-vector tested.

    Round 1 starts at (genesis + 1 * period) per drand convention —
    round 0 is the genesis pre-block and never has a signature.
    """
    unix = int(close_time.timestamp())
    if unix <= DRAND_MAINNET_GENESIS + DRAND_MAINNET_PERIOD_SECONDS:
        return 1
    elapsed = unix - DRAND_MAINNET_GENESIS
    # Ceiling division to get the first round on or after `unix`.
    return (elapsed + DRAND_MAINNET_PERIOD_SECONDS - 1) // DRAND_MAINNET_PERIOD_SECONDS


def _stub_round(close_time: datetime) -> DrandRoundEntropy:
    """Deterministic drand entropy for tests + demo-offline runs."""
    round_number = round_at_or_after(close_time)
    seed = f"drand-stub:{close_time.isoformat(timespec='microseconds')}:{round_number}"
    randomness = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    signature = hashlib.sha256((seed + ":sig").encode("utf-8")).hexdigest()
    return DrandRoundEntropy(
        round=round_number,
        randomness=randomness,
        signature=signature,
    )


async def fetch_stub(close_time: datetime) -> DrandRoundEntropy:
    return _stub_round(close_time)


async def fetch_live(close_time: datetime) -> DrandRoundEntropy:
    round_number = round_at_or_after(close_time)
    url = f"{DRAND_API_BASE}/public/{round_number}"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EntropyFetchError(
                f"drand fetch failed for round {round_number}: {exc}"
            ) from exc

    data: dict[str, Any] = response.json()
    # Drand API sanity: response `round` must match what we asked for
    # (guards against a proxy returning a stale round).
    if int(data.get("round", -1)) != round_number:
        raise EntropyFetchError(
            f"drand returned round {data.get('round')} but we asked for {round_number}"
        )
    return DrandRoundEntropy(
        round=int(data["round"]),
        randomness=str(data["randomness"]),
        signature=str(data["signature"]),
    )
