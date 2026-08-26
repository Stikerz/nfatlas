#!/usr/bin/env python3
"""Enforce the ADR-002 outbox invariant.

    Every state change that triggers work outside its own transaction
    emits an outbox event.

Run from the repo root, no arguments:

    python backend/tools/check_outbox_invariant.py

Exit 0 if the invariant holds, 1 with a diagnostic if not. Wired into the
`module-boundaries` CI job.

## Why AST and not grep

The other module-boundary checks are greps, and `ci.yaml` says so: *"Grep-only;
will be replaced by an AST check when scope grows."* This check has to answer
"does the function containing this `audit.append` also emit?", which is a
question about scope, not about text. A grep can find both calls in a file; it
cannot tell whether they are in the same function.

## What counts as a state change

Every recorded state change goes through `atlas.audit_log.writer.append` by
ADR-005 design, so `audit.append` call sites are the state-change surface. That
is the same basis as the W9 Day 1 producer inventory in `docs/events.md`, and
it is more honest than counting function signatures, which mix reads, pure
helpers and writes.

## Adding a state change

If you add an `audit.append` and CI fails here, that is the gate working. Two
correct responses:

1. The change triggers work outside the transaction (a notification, a public
   surface update, a downstream module reacting) — emit an outbox event.
2. It does not — add the event name to `ALLOWLIST` below **with a reason**.

The reason is not decoration. This allowlist is the record of which state
changes were considered and deliberately left without a producer; an allowlist
of bare names rots into a list nobody dares touch, which is how the
`get_secret_value` check sat red for four commits in W8 while enforcing nothing.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "backend" / "src" / "atlas"

# Whole modules outside the invariant.
EXCLUDED_MODULES = {
    # ADR-005: the hash chain is synchronous by design. An async audit write
    # would break the ordering the chain depends on.
    "audit_log",
    # Infrastructure. A producer that emitted about emitting would recurse.
    "outbox",
    # Infrastructure, no domain state.
    "idempotency",
}

# State changes that deliberately have no outbox producer.
# Source: docs/events.md §Producer inventory, reviewed by Winston W9 Day 1.
ALLOWLIST: dict[str, str] = {
    "otp.verified": "No work follows; the audit row is the record",
    "otp.verification_failed": "Security signal for the audit trail; no consumer",
    "user.password_set": "No consumer today; revisit if a security-notification channel lands",
    "session.created": "Login is an audit fact, not a domain event",
    "session.revoked": "As session.created",
    "payment.intent_created": "An intent is not yet money; payment.confirmed carries the consequence",
    "payment.ticket_metadata_missing": "Operator error signal; belongs in the audit trail",
    "wallet.ticket_purchase_posted": "Internal double-entry movement, no external consumer",
    "wallet.ticket_sale_recorded": "As wallet.ticket_purchase_posted",
    "wallet.payment_fee_posted": "As wallet.ticket_purchase_posted",
    "ticket.paid_purchase_completed": "Same domain moment as ticket.issued, which carries it",
    "skill_question.issued": "Question delivery is synchronous and user-facing",
    "skill_question.answered_correct": "Outcome is returned in the response; nothing follows",
    "skill_question.answered_wrong": "As skill_question.answered_correct",
    "notification.winner_selected": "This is the consumer, not a producer — it records that delivery was attempted",
    # Deferred producers: classified must-emit, but blocked. Emitting ahead of a
    # consumer dead-letters on the first attempt (outbox/worker.py), so each
    # stays here until its trigger lands. See docs/events.md §What this means.
    "user.registered": "DEFERRED — emit when a welcome/KYC-kickoff consumer exists",
    "otp.issued": "DEFERRED — cannot carry the plaintext code in a payload (otp_service.py:5). See docs/events.md rule 4",
    "payment.confirmed": "DEFERRED — emit when a receipt consumer exists",
    "payment.failed": "DEFERRED — emit when a failure-notice consumer exists",
    "wallet.deposit_credited": "DEFERRED — emit when a balance-change consumer exists",
    "wallet.prize_awarded": "DEFERRED — emit when a payout-notification consumer exists",
    "wallet.refund_issued": "DEFERRED — emit when a refund-confirmation consumer exists",
    "ticket.issued": "DEFERRED — emit when a ticket-confirmation consumer exists",
    "ticket.free_transcribed": "DEFERRED — emit when a free-route confirmation consumer exists",
    "draw.committed": "DEFERRED — emit when a public-announcement consumer exists",
    "draw.entries_snapshot": "DEFERRED — emit when a sales-closed consumer exists",
    "draw.revealed": "DEFERRED — emit when a public-surface consumer exists",
    "draw.winner_claimed": "DEFERRED — emit when a fulfilment consumer exists",
}


def _call_name(node: ast.Call) -> str:
    """`audit.append(...)` -> 'audit.append'; `emit(...)` -> 'emit'."""
    f = node.func
    if isinstance(f, ast.Attribute):
        base = f.value.id if isinstance(f.value, ast.Name) else ""
        return f"{base}.{f.attr}" if base else f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def _event_names(node: ast.Call) -> list[str]:
    """Literal event_name values, including the `a if c else b` form."""
    for kw in node.keywords:
        if kw.arg != "event_name":
            continue
        v = kw.value
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            return [v.value]
        if isinstance(v, ast.IfExp):
            out = []
            for branch in (v.body, v.orelse):
                if isinstance(branch, ast.Constant) and isinstance(branch.value, str):
                    out.append(branch.value)
            return out
    return []


def _scan(path: Path) -> list[tuple[str, int, str]]:
    """Violations in one file: (relative path, line, event name)."""
    tree = ast.parse(path.read_text())
    rel = str(path.relative_to(SRC))
    found: list[tuple[str, int, str]] = []

    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        audits: list[tuple[int, str]] = []
        emits = False
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)
            if name.endswith("audit.append") or name == "append":
                for ev in _event_names(node):
                    audits.append((node.lineno, ev))
            elif name.endswith(".emit") or name == "emit":
                emits = True
        if emits:
            continue
        for lineno, ev in audits:
            if ev not in ALLOWLIST:
                found.append((rel, lineno, ev))
    return found


def main() -> int:
    if not SRC.is_dir():
        print(f"✗ source tree not found at {SRC}", file=sys.stderr)
        return 1

    violations: list[tuple[str, int, str]] = []
    checked = 0
    for path in sorted(SRC.rglob("*.py")):
        if set(path.relative_to(SRC).parts) & EXCLUDED_MODULES:
            continue
        checked += 1
        violations.extend(_scan(path))

    if violations:
        print("::error::ADR-002 outbox invariant violated", file=sys.stderr)
        print(
            "\nThese state changes neither emit an outbox event nor appear in "
            "the allowlist:\n",
            file=sys.stderr,
        )
        for rel, line, ev in violations:
            print(f"  {rel}:{line}  {ev}", file=sys.stderr)
        print(
            "\nEither emit an outbox event (if work happens outside the "
            "transaction),\nor add the name to ALLOWLIST in "
            "backend/tools/check_outbox_invariant.py **with a reason**.\n"
            "See docs/events.md §Producer inventory.",
            file=sys.stderr,
        )
        return 1

    print(
        f"✓ ADR-002 outbox invariant holds "
        f"({checked} files checked, {len(ALLOWLIST)} allowlisted)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
