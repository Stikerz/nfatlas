#!/usr/bin/env python3
"""Regenerate the visual walkthrough — screenshots plus the page that indexes them.

Drives the real admin UI through a full draw lifecycle in headless Chromium and
writes `docs/screens/*.png` + `docs/VISUAL-WALKTHROUGH.md`. Run it after any UI
change so the walkthrough does not quietly go stale.

The backend heavy lifting (six consumers, OTP, skill questions, purchases,
signed webhooks) is delegated to `record_demo.bootstrap_pool`, the same primer
the demo recording uses, so this cannot drift from the rehearsal flow.

Usage — needs a freshly reset stack, because it closes and reveals the draw:

    make dev
    make demo-reset
    set -a; source .env; set +a
    backend/.venv/bin/python infrastructure/scripts/capture_screens.py

Add `--with-mobile` to also capture the iOS simulator, which requires a booted
device with the app already installed:

    cd mobile && flutter build ios --simulator
    xcrun simctl install booted build/ios/iphonesimulator/Runner.app
    xcrun simctl launch booted dev.atlas.atlasMobile

Requires the `demo` extra:

    backend/.venv/bin/pip install -e "backend[demo]"
    backend/.venv/bin/python -m playwright install chromium

Env: ATLAS_API_BASE, ATLAS_ADMIN_BASE, ATLAS_SUPERADMIN_EMAIL,
ATLAS_SUPERADMIN_PASSWORD (the last must match the bootstrapped operator).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "infrastructure" / "scripts"
SHOT_DIR = REPO_ROOT / "docs" / "screens"
PAGE = REPO_ROOT / "docs" / "VISUAL-WALKTHROUGH.md"

API = os.environ.get("ATLAS_API_BASE", "http://localhost:8000").rstrip("/")
ADMIN = os.environ.get("ATLAS_ADMIN_BASE", "http://localhost:3000").rstrip("/")
EMAIL = os.environ.get("ATLAS_SUPERADMIN_EMAIL", "adaobi.ibe@atlas.dev")
PASSWORD = os.environ.get(
    "ATLAS_SUPERADMIN_PASSWORD", "dev_bootstrap_password_change_me_00"
)
VIEWPORT = {"width": 1440, "height": 900}
MOBILE_BUNDLE = "dev.atlas.atlasMobile"

# One spec drives both the capture and the page, so a screenshot can never be
# added without a caption or captioned without being captured.
#
# Sections follow the draw's actual timeline rather than grouping by platform,
# because that is what the page claims to do. Consumer and operator surfaces
# genuinely interleave: someone enters on mobile before an operator can close,
# and the winner claims on mobile after the reveal. Grouping all of mobile at
# the end told a tidier story than the product actually has.
#
# `src` is "web" for a Playwright capture under docs/screens/, or "golden" for
# a Flutter golden referenced in place under mobile/test/design/goldens/.
# `stage` is the draw state the surface belongs to.
SECTIONS: list[dict] = [
    {
        "heading": "1 · The promise, before anyone has entered",
        "intro": (
            "The public surface exists to be checked by someone who does not "
            "trust you. It states the free-entry route and the skill question "
            "up front rather than burying them."
        ),
        "shots": [
            {"src": "web", "file": "01-how-it-works.png", "stage": "public",
             "title": "How it works",
             "note": "The commit-reveal protocol in plain language. Atlas is a "
                     "prize competition, not a lottery — every draw carries a "
                     "free entry route with identical odds, and that claim is "
                     "made here."},
            {"src": "web", "file": "02-responsible-play.png", "stage": "public",
             "title": "Responsible play",
             "note": "Self-exclusion and spend limits. Required by the "
                     "positioning, not bolted on after."},
            {"src": "web", "file": "03-proof-sealed.png", "stage": "sealed",
             "title": "Public proof — sealed",
             "note": "The commitment (SHA-256 of the server seed and draw id) "
                     "is published when the draw is created. The seed itself "
                     "is withheld and encrypted at rest. Anyone can record "
                     "this hash now and hold Atlas to it later."},
        ],
    },
    {
        "heading": "2 · Entering — the consumer, on mobile",
        "intro": (
            "Nothing can be closed or revealed until people have entered, so "
            "this comes before the operator surfaces rather than after them."
        ),
        "shots": [
            {"src": "golden", "file": "register.png", "stage": "sales_open",
             "title": "Register",
             "note": "The +234 prefix is fixed rather than a country picker, "
                     "date of birth gates at 18, and terms are an explicit "
                     "checkbox rather than implied consent."},
            {"src": "golden", "file": "otp.png", "stage": "sales_open",
             "title": "One-time code",
             "note": "Delivered to Mailhog in V0.5 rather than by SMS."},
            {"src": "golden", "file": "password.png", "stage": "sales_open",
             "title": "Set a password",
             "note": "Two rules gate the button — ten characters, and a mix of "
                     "letters and numbers. The third line is advisory and "
                     "always passes."},
            {"src": "golden", "file": "welcome.png", "stage": "sales_open",
             "title": "Welcome",
             "note": "Auto-advances to Home after 800ms, which is why its "
                     "golden is captured at 300ms."},
            {"src": "golden", "file": "home.png", "stage": "sales_open",
             "title": "Home",
             "note": "Wallet chip, the active draw, and the commitment shown "
                     "to the consumer before the reveal — the same hash the "
                     "public proof page publishes."},
            {"src": "golden", "file": "skill-question.png", "stage": "sales_open",
             "title": "Skill question",
             "note": "Mandatory on every paid entry. This is the mechanism "
                     "that makes Atlas a prize competition rather than a "
                     "lottery, so it is a gate rather than a formality."},
        ],
    },
    {
        "heading": "3 · Closing and revealing — the operator",
        "intro": (
            "A draw moves through a state machine and the console offers only "
            "the actions the current state permits. Watch the action set "
            "change on the same screen across the next four shots — that is "
            "the machine, not a tour of it."
        ),
        "shots": [
            {"src": "web", "file": "04-login.png", "stage": "auth",
             "title": "Operator login",
             "note": "Reaching `/` redirects here. Until W8 the middleware "
                     "guard was never loaded — it sat one directory above the "
                     "app — so `/` returned 404 and the guard did nothing."},
            {"src": "web", "file": "05-dashboard.png", "stage": "auth",
             "title": "Dashboard",
             "note": "Landing surface after sign-in."},
            {"src": "web", "file": "06-draws-list.png", "stage": "index",
             "title": "Draws",
             "note": "The operator draw index. The sidebar shows the full "
                     "planned operator surface; seven of those links have no "
                     "page yet and 404 today."},
            {"src": "web", "file": "07-draw-open.png", "stage": "sales_open",
             "title": "Draw detail — sales open",
             "note": "The commitment is shown to the operator pre-reveal, the "
                     "same value the public page carries. Only **Close draw** "
                     "is offered; reveal is not reachable from this state."},
            {"src": "web", "file": "08-confirm.png", "stage": "sales_open",
             "title": "Confirming an irreversible action",
             "note": "Every lifecycle action is two-step. The copy says *this "
                     "is not reversible* because it is not — a closed draw "
                     "cannot reopen and a revealed one cannot be re-revealed."},
            {"src": "web", "file": "09-draw-closed.png", "stage": "sales_closed",
             "title": "Draw detail — sales closed",
             "note": "State advanced, and the action set with it. Close is "
                     "gone; reveal is the only move."},
            {"src": "web", "file": "10-draw-revealed.png", "stage": "revealed",
             "title": "Draw detail — revealed",
             "note": "Winners selected, draw terminal. The reveal writes an "
                     "outbox row in the same transaction; the worker "
                     "dispatched it in ~0.1s. The only remaining action is a "
                     "link to the public proof."},
        ],
    },
    {
        "heading": "4 · Checking the result — anyone",
        "intro": (
            "The point of the protocol: the result can be checked by someone "
            "with no account and no reason to believe Atlas."
        ),
        "shots": [
            {"src": "web", "file": "12-proof-open.png", "stage": "revealed",
             "title": "Public proof — opened",
             "note": "The same URL as the sealed shot in section 1, now "
                     "carrying the server seed, the drand round and "
                     "randomness, the tickets hash and the full winner list. "
                     "The commitment published earlier still matches."},
            {"src": "web", "file": "13-verify.png", "stage": "revealed",
             "title": "Verify it yourself",
             "note": "Copy the command, run it against the published proof, "
                     "recompute the winner independently. The verifier is "
                     "standalone and needs nothing from Atlas."},
            {"src": "web", "file": "11-audit-log.png", "stage": "audit",
             "title": "Hash-chained audit log",
             "note": "Every event carries the hash of the one before it "
                     "(ADR-005). Alter a historical row and every subsequent "
                     "hash breaks, which the chain check catches on read. That "
                     "is what makes the log evidence rather than a list."},
        ],
    },
    {
        "heading": "5 · Claiming — the winner, back on mobile",
        "intro": "",
        "shots": [
            {"src": "golden", "file": "winner-claim.png", "stage": "revealed",
             "title": "Winner claim",
             "note": "Rendered from the intersection of the tickets a user "
                     "owns and the draw's winner list, so a user who holds no "
                     "winning ticket sees the empty state instead."},
        ],
    },
]

MOBILE_SHOT = {
    "file": "m01-register.png",
    "title": "The app running on an iOS simulator",
    "note": (
        "Everything in section 2 and section 5 is a Flutter golden — a widget "
        "render, not a device. This is the same build on a booted simulator, "
        "device chrome and all, as evidence the app runs rather than merely "
        "paints."
    ),
}

GOLDEN_DIR = "../mobile/test/design/goldens"


def log(msg: str) -> None:
    print(f"[capture] {msg}", flush=True)


def die(msg: str) -> None:
    print(f"\n✗ {msg}\n", file=sys.stderr)
    raise SystemExit(1)


def preflight() -> None:
    for name, url in (("backend", f"{API}/healthz"), ("admin", ADMIN)):
        try:
            urllib.request.urlopen(url, timeout=10).close()
        except Exception as exc:  # noqa: BLE001 — any failure means it's down
            die(f"{name} not reachable at {url} ({exc}). Run `make dev` first.")
    log("preflight ok")


def prime_pool() -> str:
    sys.path.insert(0, str(SCRIPTS))
    import record_demo

    cfg = record_demo.Config.from_env()
    return asyncio.run(record_demo.bootstrap_pool(cfg))


def assert_sales_open(draw_id: str) -> None:
    with urllib.request.urlopen(f"{API}/api/v1/draws/{draw_id}", timeout=10) as r:
        state = json.load(r).get("state")
    if state != "sales_open":
        die(
            f"draw {draw_id} is {state!r}, expected 'sales_open'. "
            "Run `make demo-reset` for a clean slate."
        )


async def capture_web(draw_id: str) -> None:
    from playwright.async_api import async_playwright

    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    # Tall pages need the full document; the rest read better cropped to the fold.
    full_page = {"01-how-it-works.png", "02-responsible-play.png",
                 "11-audit-log.png", "12-proof-open.png"}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(
            viewport=VIEWPORT,
            # The /proof verify block writes to the clipboard; without this the
            # click is swallowed and the button never shows its "Copied" state.
            permissions=["clipboard-read", "clipboard-write"],
        )
        ctx.set_default_timeout(30_000)
        page = await ctx.new_page()

        async def snap(name: str) -> None:
            await page.wait_for_timeout(700)
            await page.screenshot(
                path=str(SHOT_DIR / name), full_page=name in full_page
            )
            log(f"  {name}")

        await page.goto(f"{ADMIN}/how-it-works", wait_until="networkidle")
        await snap("01-how-it-works.png")
        await page.goto(f"{ADMIN}/responsible-play", wait_until="networkidle")
        await snap("02-responsible-play.png")
        await page.goto(f"{ADMIN}/proof/{draw_id}", wait_until="networkidle")
        await snap("03-proof-sealed.png")

        await page.goto(f"{ADMIN}/login", wait_until="networkidle")
        await snap("04-login.png")
        # Role+name, not get_by_label: the password field ships with a
        # "Show password" toggle whose aria-label also matches, which trips
        # Playwright strict mode.
        await page.get_by_role("textbox", name="Email").fill(EMAIL)
        await page.get_by_role("textbox", name="Password").fill(PASSWORD)
        await page.get_by_role("button", name="Sign in").click()
        await page.wait_for_url(re.compile(r"/admin"))
        await page.wait_for_load_state("networkidle")
        await snap("05-dashboard.png")

        await page.goto(f"{ADMIN}/admin/draws", wait_until="networkidle")
        await snap("06-draws-list.png")
        await page.goto(f"{ADMIN}/admin/draws/{draw_id}", wait_until="networkidle")
        await snap("07-draw-open.png")

        await page.get_by_role("button", name="Close draw").click()
        await page.wait_for_timeout(400)
        await snap("08-confirm.png")
        await page.get_by_role("button", name="Yes, close draw").click()
        await page.get_by_role("button", name="Reveal winner").wait_for(state="visible")
        await page.wait_for_load_state("networkidle")
        await snap("09-draw-closed.png")

        await page.get_by_role("button", name="Reveal winner").click()
        await page.wait_for_timeout(400)
        await page.get_by_role("button", name="Yes, reveal winner").click()
        await page.get_by_role("link", name=re.compile("View public proof")).wait_for(
            state="visible"
        )
        await page.wait_for_load_state("networkidle")
        await snap("10-draw-revealed.png")

        await page.goto(f"{ADMIN}/admin/audit-log", wait_until="networkidle")
        await snap("11-audit-log.png")
        await page.goto(f"{ADMIN}/proof/{draw_id}", wait_until="networkidle")
        await snap("12-proof-open.png")

        copy = page.get_by_role("button", name="Copy verify command")
        if await copy.count():
            await copy.first.scroll_into_view_if_needed()
            await copy.first.click()
            # CopyCommand reverts to "Copy" after 2000ms; hold short of it.
            await page.wait_for_timeout(1_200)
            await snap("13-verify.png")

        await ctx.close()
        await browser.close()


def capture_mobile() -> bool:
    """Best-effort iOS simulator shot. Returns False if no device is usable."""
    try:
        devices = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "booted"],
            capture_output=True, text=True, check=True,
        ).stdout
    except Exception:  # noqa: BLE001 — no Xcode, not an error
        log("mobile: xcrun unavailable, skipping")
        return False
    if "Booted" not in devices:
        log("mobile: no booted simulator, skipping")
        return False
    subprocess.run(["xcrun", "simctl", "launch", "booted", MOBILE_BUNDLE],
                   capture_output=True, text=True, check=False)
    result = subprocess.run(
        ["xcrun", "simctl", "io", "booted", "screenshot",
         str(SHOT_DIR / MOBILE_SHOT["file"])],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        log(f"mobile: screenshot failed — {result.stderr.strip()}")
        return False
    log(f"  {MOBILE_SHOT['file']}")
    return True


def validate_spec() -> None:
    """Keep SECTIONS and the capture sequence honest about each other.

    capture_web() drives the browser in a fixed order rather than iterating
    SECTIONS, so the two can drift: a shot could be captured with no caption,
    or captioned and never captured. Checking both directions after the fact
    is what makes the "one spec" claim in the module docstring true.
    """
    web = {s["file"] for sec in SECTIONS for s in sec["shots"]
           if s.get("src") == "web"}
    golden = {s["file"] for sec in SECTIONS for s in sec["shots"]
              if s.get("src") == "golden"}

    missing_golden = [
        f for f in sorted(golden)
        if not (REPO_ROOT / "mobile" / "test" / "design" / "goldens" / f).exists()
    ]
    if missing_golden:
        die(
            "captioned goldens do not exist: "
            + ", ".join(missing_golden)
            + "\nRun: cd mobile && flutter test "
            "test/design/screen_goldens_test.dart --update-goldens"
        )
    globals()["_EXPECTED_WEB"] = web


def verify_captures() -> None:
    """Every captioned web shot exists, and nothing extra is lying around."""
    expected = globals().get("_EXPECTED_WEB", set())
    on_disk = {p.name for p in SHOT_DIR.glob("*.png")}
    missing = sorted(expected - on_disk)
    if missing:
        die("captioned but not captured: " + ", ".join(missing))
    extra = sorted(on_disk - expected - {MOBILE_SHOT["file"]})
    if extra:
        log(f"warning: captured but not captioned, so unused: {', '.join(extra)}")


def write_page() -> None:
    def img(shot: dict) -> str:
        if shot.get("src") == "golden":
            return f"{GOLDEN_DIR}/{shot['file']}"
        return f"screens/{shot['file']}"

    def block(shot: dict) -> str:
        chip = f"`{shot['stage']}`\n\n" if shot.get("stage") else ""
        return (
            f"### {shot['title']}\n\n"
            f"{chip}"
            f"{shot['note']}\n\n"
            f"![{shot['title']}]({img(shot)})\n"
        )

    parts = [
        "# Visual walkthrough",
        "",
        "Every Atlas surface, in the order a draw passes through them — which",
        "means consumer and operator screens interleave rather than being grouped",
        "by platform. Someone has to enter before an operator can close, and the",
        "winner claims after the reveal.",
        "",
        "Captured from a running local stack: real Postgres, six registered",
        "consumers, a genuine commit-reveal cycle. Nothing here is a mockup.",
        "",
        "| | |",
        "|---|---|",
        "| Web surfaces | Playwright against the running admin, in `docs/screens/` |",
        "| Mobile surfaces | Flutter goldens, in `mobile/test/design/goldens/` |",
        "| Regenerate web | `infrastructure/scripts/capture_screens.py` |",
        "| Regenerate mobile | `cd mobile && flutter test test/design/screen_goldens_test.dart --update-goldens` |",
        "",
        "Because the mobile shots are goldens, a UI change shows up as an image",
        "diff in the pull request that caused it.",
        "",
    ]
    for section in SECTIONS:
        parts += [f"## {section['heading']}", ""]
        if section["intro"]:
            parts += [section["intro"], ""]
        for shot in section["shots"]:
            parts += [block(shot), ""]

    parts += ["---", "", "## How these were captured", ""]
    if (SHOT_DIR / MOBILE_SHOT["file"]).exists():
        parts += [
            MOBILE_SHOT["note"],
            "",
            f"![{MOBILE_SHOT['title']}](screens/{MOBILE_SHOT['file']})",
            "",
        ]
    parts += [
        "The web shots are driven through a real draw lifecycle by Playwright,",
        "reusing `record_demo.bootstrap_pool` so the flow cannot drift from the",
        "rehearsal script. The mobile goldens render real typography because the",
        "faces are bundled under `mobile/assets/google_fonts/` rather than fetched",
        "at runtime.",
        "",
        "Palette and type are the Atlas tokens in",
        "[`_bmad-output/planning-artifacts/design/tokens.md`](../_bmad-output/planning-artifacts/design/tokens.md)",
        "— navy `#0F1E38`, brass `#C9A96A`, Fraunces and Inter.",
        "",
    ]
    PAGE.write_text("\n".join(parts))
    log(f"wrote {PAGE.relative_to(REPO_ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--with-mobile", action="store_true",
                    help="Also screenshot a booted iOS simulator running the app.")
    ap.add_argument("--page-only", action="store_true",
                    help="Regenerate the markdown from existing screenshots.")
    args = ap.parse_args()

    if args.page_only:
        validate_spec()
        write_page()
        return 0

    preflight()
    validate_spec()
    draw_id = prime_pool()
    assert_sales_open(draw_id)
    log(f"capturing web surfaces for draw {draw_id}")
    asyncio.run(capture_web(draw_id))
    if args.with_mobile:
        capture_mobile()
    verify_captures()
    write_page()

    total = sum(p.stat().st_size for p in SHOT_DIR.glob("*.png"))
    print(f"\n✓ {len(list(SHOT_DIR.glob('*.png')))} screenshots, "
          f"{total / 1024 / 1024:.1f} MB in {SHOT_DIR.relative_to(REPO_ROOT)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
