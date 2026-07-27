"""Public-entropy adapters (ADR-006 §Protocol stage 4).

Two independent primitives combine to form the reveal-time seed:
  - Bitcoin: block-header hash for the block whose timestamp is the
    smallest ≥ close_time. Cross-checked across two independent
    explorers (mempool.space + blockstream.info).
  - drand: League of Entropy randomness for the round whose epoch is
    the smallest ≥ close_time.

`ATLAS_DRAW_ENTROPY_MODE`:
  stub  (default in tests + CI): deterministic canned values per
        close_time. No network. Verifier CLI reproducible.
  live  (demo dev + prod): real HTTP fetch from public endpoints.
        Production must set live per the config prod-safety validator.
"""
