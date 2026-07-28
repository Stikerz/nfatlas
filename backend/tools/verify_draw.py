#!/usr/bin/env python3
"""Standalone draw-proof verifier CLI.

Given a proof JSON blob (from `GET /api/v1/draws/{id}/proof` on a
revealed draw), re-runs the winner-selection algorithm and confirms
the recomputed winner matches the published winner. Third parties can
run this without touching the Atlas backend — the only dependency is
Python's stdlib (for --proof PATH) or the standard `urllib.request`
module (for --proof-url URL).

Exit codes:
  0  proof reproduces the published winner (and reserves)
  1  proof mismatch — recomputed winner differs from published
  2  invalid arguments / proof shape / not-yet-revealed proof
  3  fetch failure (--proof-url could not be retrieved)

Usage:

    python backend/tools/verify_draw.py --proof path/to/proof.json
    python backend/tools/verify_draw.py \\
        --proof-url http://localhost:8000/api/v1/draws/{uuid}/proof
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

# Path munge so the CLI works without pip-installing the package.
_repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo_root / "backend" / "src"))

from atlas.draw.reveal import select_winners  # noqa: E402


def _fetch_proof(url: str) -> dict[str, Any]:
    try:
        with urlopen(
            Request(url, headers={"Accept": "application/json"}), timeout=10
        ) as response:
            payload: dict[str, Any] = json.load(response)
            return payload
    except URLError as exc:
        print(f"error: could not fetch proof from {url}: {exc}", file=sys.stderr)
        sys.exit(3)


def _read_proof(path: Path) -> dict[str, Any]:
    if not path.exists():
        print(f"error: proof file not found: {path}", file=sys.stderr)
        sys.exit(2)
    with path.open() as handle:
        payload: dict[str, Any] = json.load(handle)
        return payload


def _verify(proof: dict[str, Any]) -> int:
    """Return exit code: 0 match, 1 mismatch, 2 invalid proof."""
    if proof.get("state") != "revealed":
        print(
            f"error: proof is for a draw in state {proof.get('state')!r}; "
            "only revealed draws can be verified.",
            file=sys.stderr,
        )
        return 2

    for field in (
        "server_seed",
        "tickets_hash",
        "ordered_ticket_ids",
        "entropy",
        "winners",
    ):
        if proof.get(field) is None:
            print(f"error: proof missing required field {field!r}", file=sys.stderr)
            return 2

    entropy = proof["entropy"]
    server_seed = bytes.fromhex(proof["server_seed"])
    tickets_hash = bytes.fromhex(proof["tickets_hash"])
    entropy_bytes = bytes.fromhex(entropy["bitcoin_hash"]) + bytes.fromhex(
        entropy["drand_randomness"]
    )
    ordered_ids = [uuid.UUID(t) for t in proof["ordered_ticket_ids"]]
    reserves = int(proof.get("reserves") or (len(proof["winners"]) - 1))

    recomputed = select_winners(
        server_seed=server_seed,
        entropy=entropy_bytes,
        tickets_hash=tickets_hash,
        ordered_ticket_ids=ordered_ids,
        reserves=reserves,
    )
    published = [uuid.UUID(w["ticket_id"]) for w in proof["winners"]]

    if recomputed != published:
        print("MISMATCH — recomputed winners differ from published proof.")
        print("  position | recomputed                             | published")
        print("  ---------+----------------------------------------+" + "-" * 40)
        for i, (r, p) in enumerate(zip(recomputed, published, strict=True)):
            marker = "✓" if r == p else "✗"
            print(f"  {i:>8} | {r} | {p} {marker}")
        return 1

    print(f"MATCH — recomputed {len(recomputed)} winners, all match published proof.")
    print(f"  primary  : {recomputed[0]}")
    for i, ticket_id in enumerate(recomputed[1:], start=1):
        print(f"  reserve {i}: {ticket_id}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify a published Atlas draw proof by re-running the winner-"
            "selection algorithm."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--proof", type=Path, help="Path to a proof JSON file on disk."
    )
    source.add_argument(
        "--proof-url",
        type=str,
        help="URL of a proof endpoint (e.g. https://.../api/v1/draws/{id}/proof).",
    )
    args = parser.parse_args()

    proof = _read_proof(args.proof) if args.proof else _fetch_proof(args.proof_url)
    return _verify(proof)


if __name__ == "__main__":
    raise SystemExit(main())
