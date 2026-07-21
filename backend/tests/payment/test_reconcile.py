"""Unit tests for the reconcile diff helper.

The nightly cron + Paystack settlement fetch land Week 6; this file
covers only `compute_diff`, which is pure and stateless.
"""

from __future__ import annotations

from datetime import date

from atlas.payment.jobs.reconcile import (
    ReconciliationDiff,
    SettlementLine,
    compute_diff,
)


def test_balanced_report_within_tolerance() -> None:
    result = compute_diff(
        day=date(2026, 7, 21),
        ledger_sum_minor=500_00,
        ledger_vendor_refs={"atlas-a"},
        settlement_lines=[
            SettlementLine(vendor_reference="atlas-a", amount_minor=500_00, fee_minor=100_00),
        ],
    )
    assert result.difference_minor == 0
    assert result.unmatched_vendor_refs == ()
    assert result.within_tolerance is True


def test_shortfall_flagged() -> None:
    """Ledger has less than the settlement — payment landed at Paystack but
    the webhook never credited our wallet."""
    result = compute_diff(
        day=date(2026, 7, 21),
        ledger_sum_minor=400_00,
        ledger_vendor_refs={"atlas-a"},
        settlement_lines=[
            SettlementLine(vendor_reference="atlas-a", amount_minor=400_00, fee_minor=0),
            SettlementLine(vendor_reference="atlas-b", amount_minor=100_00, fee_minor=0),
        ],
    )
    assert result.difference_minor == -100_00
    assert result.unmatched_vendor_refs == ("atlas-b",)
    assert result.within_tolerance is False


def test_penny_drift_within_default_tolerance() -> None:
    """₦1 tolerance covers legitimate rounding — the ₦100 default is
    a shape-check, not a strict-match."""
    result = compute_diff(
        day=date(2026, 7, 21),
        ledger_sum_minor=500_50,
        ledger_vendor_refs={"atlas-a"},
        settlement_lines=[
            SettlementLine(vendor_reference="atlas-a", amount_minor=500_00, fee_minor=0),
        ],
    )
    assert result.difference_minor == 50
    assert result.within_tolerance is True


def test_returns_frozen_dataclass_shape() -> None:
    result = compute_diff(
        day=date(2026, 7, 21),
        ledger_sum_minor=0,
        ledger_vendor_refs=set(),
        settlement_lines=[],
    )
    assert isinstance(result, ReconciliationDiff)
    assert result.day == date(2026, 7, 21)
