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
# added without a caption or captioned without being captured. `stage` is the
# draw state the shot was taken in, or the surface type for non-draw screens.
SECTIONS: list[dict] = [
    {
        "heading": "Before the draw opens",
        "intro": (
            "The public surface exists to be checked by someone who does not trust "
            "you. It states the free-entry route and the skill question up front "
            "rather than burying them."
        ),
        "shots": [
            {
                "file": "01-how-it-works.png",
                "stage": "public",
                "title": "How it works",
                "note": (
                    "The commit-reveal protocol in plain language. Atlas is a prize "
                    "competition, not a lottery — every draw carries a free entry "
                    "route with identical odds, and that claim is made here."
                ),
            },
            {
                "file": "02-responsible-play.png",
                "stage": "public",
                "title": "Responsible play",
                "note": "Self-exclusion and spend limits. Required by the positioning, not bolted on after.",
            },
            {
                "file": "03-proof-sealed.png",
                "stage": "sealed",
                "title": "Public proof, before the reveal",
                "note": (
                    "The commitment — SHA-256 of the server seed and draw id — is "
                    "published when the draw is created. The seed itself is withheld "
                    "and encrypted at rest. Anyone can record this hash now and hold "
                    "Atlas to it later."
                ),
            },
        ],
    },
    {
        "heading": "The operator lifecycle",
        "intro": (
            "A draw moves through a state machine and the console offers only the "
            "actions the current state permits. The sequence below is that machine, "
            "not a tour — note how the action set changes on the same screen."
        ),
        "shots": [
            {
                "file": "04-login.png",
                "stage": "auth",
                "title": "Operator login",
                "note": (
                    "Reaching `/` redirects here. Until W8 the middleware guard was "
                    "never loaded — it sat one directory above the app — so `/` "
                    "returned 404 and the guard did nothing."
                ),
            },
            {
                "file": "05-dashboard.png",
                "stage": "auth",
                "title": "Dashboard",
                "note": "Landing surface after sign-in.",
            },
            {
                "file": "06-draws-list.png",
                "stage": "index",
                "title": "Draws",
                "note": "The operator draw index.",
            },
            {
                "file": "07-draw-open.png",
                "stage": "sales_open",
                "title": "Draw detail — sales open",
                "note": (
                    "The commitment is shown to the operator pre-reveal, the same "
                    "value the public page carries. Only **Close draw** is offered; "
                    "reveal is not reachable from this state."
                ),
            },
            {
                "file": "08-confirm.png",
                "stage": "sales_open",
                "title": "Confirming an irreversible action",
                "note": (
                    "Every lifecycle action is two-step. The copy says *this is not "
                    "reversible* because it is not — a closed draw cannot reopen and "
                    "a revealed one cannot be re-revealed."
                ),
            },
            {
                "file": "09-draw-closed.png",
                "stage": "sales_closed",
                "title": "Draw detail — sales closed",
                "note": "State advanced, and the action set with it. Close is gone; reveal is the only move.",
            },
            {
                "file": "10-draw-revealed.png",
                "stage": "revealed",
                "title": "Draw detail — revealed",
                "note": (
                    "Winners selected, draw terminal. The reveal writes an outbox row "
                    "in the same transaction; the worker dispatched it in ~0.1s. The "
                    "only remaining action is a link to the public proof."
                ),
            },
        ],
    },
    {
        "heading": "After the reveal",
        "intro": "",
        "shots": [
            {
                "file": "12-proof-open.png",
                "stage": "revealed",
                "title": "Public proof, opened",
                "note": (
                    "The same URL as the sealed shot above, now carrying the server "
                    "seed, the drand round and randomness, the tickets hash and the "
                    "full winner list. The commitment published earlier still matches."
                ),
            },
            {
                "file": "13-verify.png",
                "stage": "revealed",
                "title": "Verify it yourself",
                "note": (
                    "The trust story in one control. Copy the command, run it against "
                    "the published proof, recompute the winner independently — the "
                    "verifier is standalone and needs nothing from Atlas."
                ),
            },
            {
                "file": "11-audit-log.png",
                "stage": "audit",
                "title": "Hash-chained audit log",
                "note": (
                    "Every event carries the hash of the one before it (ADR-005). "
                    "Alter a historical row and every subsequent hash breaks, which "
                    "the chain check catches on read. That is what makes the log "
                    "evidence rather than a list."
                ),
            },
        ],
    },
]

MOBILE_SHOT = {
    "file": "m01-register.png",
    "stage": "simulator",
    "title": "Running on an iOS simulator",
    "note": (
        "The real app on a device, device chrome and all — proof it runs, not "
        "just that its widgets paint."
    ),
}

# Every consumer screen, rendered by mobile/test/design/screen_goldens_test.dart
# and referenced in place rather than copied, so regenerating the goldens
# (`flutter test test/design/screen_goldens_test.dart --update-goldens`)
# updates this page with no second step and no chance of a stale duplicate.
GOLDEN_DIR = "../mobile/test/design/goldens"
MOBILE_GOLDENS: list[dict] = [
    {"file": "register.png", "title": "Register",
     "note": "The +234 prefix is fixed rather than a country picker, date of "
             "birth gates at 18, and terms are an explicit checkbox."},
    {"file": "otp.png", "title": "One-time code",
     "note": "Delivered to Mailhog in V0.5 rather than by SMS."},
    {"file": "password.png", "title": "Set a password",
     "note": "Two rules gate the button — ten characters and a letter/number "
             "mix. The third line is advisory and always passes."},
    {"file": "welcome.png", "title": "Welcome",
     "note": "Auto-advances to Home after 800ms, which is why its golden is "
             "captured at 300ms."},
    {"file": "home.png", "title": "Home",
     "note": "Wallet chip, the active draw, and the commitment shown to the "
             "consumer before the reveal — the same hash the public proof "
             "page publishes."},
    {"file": "skill-question.png", "title": "Skill question",
     "note": "Mandatory on every paid entry. This is the mechanism that makes "
             "Atlas a prize competition rather than a lottery."},
    {"file": "winner-claim.png", "title": "Winner claim",
     "note": "Post-reveal claim surface."},
]


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


def write_page() -> None:
    def block(shot: dict) -> str:
        return (
            f"### {shot['title']}\n\n"
            f"`{shot['stage']}`\n\n"
            f"{shot['note']}\n\n"
            f"![{shot['title']}](screens/{shot['file']})\n"
        )

    parts = [
        "# Visual walkthrough",
        "",
        "Every Atlas surface, in the order a draw passes through them. Captured from",
        "a running local stack — real Postgres, six registered consumers, a genuine",
        "commit-reveal cycle. Nothing here is a mockup.",
        "",
        "Regenerate with `infrastructure/scripts/capture_screens.py` after any UI",
        "change; see that file's docstring for prerequisites.",
        "",
    ]
    for section in SECTIONS:
        parts += [f"## {section['heading']}", ""]
        if section["intro"]:
            parts += [section["intro"], ""]
        for shot in section["shots"]:
            parts += [block(shot), ""]

    parts += [
        "## Mobile",
        "",
        "Every consumer screen, rendered from",
        "`mobile/test/design/screen_goldens_test.dart`. These are golden files, so a UI",
        "change shows up as an image diff in the pull request that caused it. Refresh",
        "them with:",
        "",
        "```bash",
        "cd mobile && flutter test test/design/screen_goldens_test.dart --update-goldens",
        "```",
        "",
        "They render real typography because the faces are bundled under",
        "`mobile/assets/google_fonts/` rather than fetched at runtime.",
        "",
    ]
    for shot in MOBILE_GOLDENS:
        parts += [
            (
                f"### {shot['title']}\n\n"
                f"{shot['note']}\n\n"
                f"![{shot['title']}]({GOLDEN_DIR}/{shot['file']})\n"
            ),
            "",
        ]
    if (SHOT_DIR / MOBILE_SHOT["file"]).exists():
        parts += [block(MOBILE_SHOT), ""]

    parts += [
        "---",
        "",
        "Palette and type throughout are the Atlas tokens in",
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
        write_page()
        return 0

    preflight()
    draw_id = prime_pool()
    assert_sales_open(draw_id)
    log(f"capturing web surfaces for draw {draw_id}")
    asyncio.run(capture_web(draw_id))
    if args.with_mobile:
        capture_mobile()
    write_page()

    total = sum(p.stat().st_size for p in SHOT_DIR.glob("*.png"))
    print(f"\n✓ {len(list(SHOT_DIR.glob('*.png')))} screenshots, "
          f"{total / 1024 / 1024:.1f} MB in {SHOT_DIR.relative_to(REPO_ROOT)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
