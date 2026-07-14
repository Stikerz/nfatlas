"""V0.5 seed data loader — SKELETON.

Populated as modules land Weeks 4-6:
  Week 4: seed a demo Paystack test-mode wallet + ledger accounts.
  Week 5: seed a demo draw (open, with a prize + skill question pool)
          plus a handful of test-user tickets.
  Week 6: seed a closed draw pending reveal for demo-day scripting.

Usage (once populated):
    docker compose run --rm backend \
        python /infrastructure/scripts/seed_v0_5.py

For Week 3, the only meaningful "seed" is the superadmin; see
bootstrap_superadmin.py.
"""

from __future__ import annotations

import sys


def main() -> None:
    sys.stderr.write(
        "seed_v0_5.py is a placeholder — no seed data exists in Week 3.\n"
        "Run bootstrap_superadmin.py to create the seeded operator, "
        "and start Amelia's Week 4 draw + ticket seeds after they land.\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
