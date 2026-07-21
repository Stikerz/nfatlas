"""Nightly Paystack reconciliation — Week 4 skeleton, Week 6 wiring.

Per ADR-008 §Settlement reconciliation:
  1. Fetch Paystack settlement report for the prior day.
  2. Sum credits to payment_gateway_clearing for that day.
  3. Compare; difference beyond tolerance triggers SEV-1 + Compliance
     review per docs/qa/strategy.md.

Only the diffing helper is complete this week. The fetch + cron wiring
land Week 6 when the outbox refactor also lands.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SettlementLine:
    """One line from a Paystack settlement report (Week 6 shape)."""

    vendor_reference: str
    amount_minor: int         # gross, kobo
    fee_minor: int            # kobo


@dataclass(frozen=True)
class ReconciliationDiff:
    """Result of comparing a settlement report against ledger sums."""

    day: date
    ledger_total_minor: int
    settlement_total_minor: int
    difference_minor: int     # ledger minus settlement; positive means over-credit
    unmatched_vendor_refs: tuple[str, ...]
    within_tolerance: bool


def compute_diff(
    *,
    day: date,
    ledger_sum_minor: int,
    ledger_vendor_refs: set[str],
    settlement_lines: list[SettlementLine],
    tolerance_minor: int = 100,  # ₦1 default tolerance
) -> ReconciliationDiff:
    """Compare a Paystack settlement day against our ledger for that day.

    `ledger_sum_minor` is the SUM of amount_minor for entries into
    payment_gateway_clearing (Paystack) posted on `day`. `ledger_vendor_refs`
    is the set of vendor_references seen in those entries. Both are
    computed by the caller from ledger_entries — this helper is pure.

    A vendor_ref in the settlement report but not in our ledger is a
    strong signal of a missed webhook (payment succeeded at Paystack but
    we never credited the user). The reverse — a ref in our ledger but
    not in the report — is normally a same-day payment that will settle
    the next day; Week 6's caller filters by report date to avoid false
    positives.
    """
    settlement_total = sum(line.amount_minor for line in settlement_lines)
    settlement_refs = {line.vendor_reference for line in settlement_lines}
    unmatched = tuple(sorted(settlement_refs - ledger_vendor_refs))
    difference = ledger_sum_minor - settlement_total

    return ReconciliationDiff(
        day=day,
        ledger_total_minor=ledger_sum_minor,
        settlement_total_minor=settlement_total,
        difference_minor=difference,
        unmatched_vendor_refs=unmatched,
        within_tolerance=abs(difference) <= tolerance_minor and not unmatched,
    )


async def run_nightly_reconciliation(day: date) -> ReconciliationDiff:
    """TODO(week-6): fetch Paystack settlement report + compute + alert.

    Week 4 leaves the signature so the cron wiring can be added in one
    commit later. Not called by anything yet.
    """
    raise NotImplementedError(
        "run_nightly_reconciliation ships Week 6 with the outbox refactor "
        "and the settlement-report fetch client."
    )
