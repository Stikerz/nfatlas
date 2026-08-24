# Runbook: Record the flagship demo via OBS (Playwright fallback)

**Severity:** N/A — this is a demo-prep procedure, not an incident.
**Owner:** Founder (S1408661) or whoever is presenting the demo.
**Last verified:** 2026-08-24 by 💻 Amelia (W8 Day 4 first draft — see `_bmad-output/implementation-artifacts/week-8-build-plan.md §Day 4`).
**Applies to:** any moment the automated `infrastructure/scripts/record_demo.py` path is unavailable (Chromium download blocked by corporate proxy, Colima/Docker down, or laptop out of scope for the automated flow). This runbook is the always-works fallback; the automated path is preferred when it works.
**Related:** `week-8-build-plan.md §Day 4`, `_bmad-output/planning-artifacts/v0.5-demo-plan.md §2` (the 16-step flagship-flow spec), `infrastructure/scripts/record_demo.py` (the codified target).

## Purpose

Produce `_bmad-output/demo/atlas-hero-flow.mp4` — a screen recording of the flagship flow (admin login → close draw → reveal winner → public `/proof` copy-verify) suitable for investor share-outs when a live demo isn't feasible or as a fallback if the live stack misbehaves mid-pitch.

The automated script `infrastructure/scripts/record_demo.py` produces the same artefact via headless Chromium. This runbook is the manual equivalent — same visual surfaces, same beats, driven by a human clicking through the admin browser tab while OBS captures the screen.

## Prereqs

1. **Local stack up and green** — `make dev` running in a spare terminal, `docker compose ps` shows `atlas-backend`, `atlas-worker`, `atlas-admin`, `atlas-mailhog`, `atlas-postgres`, `atlas-redis` all healthy.
2. **Fresh seed** — `make demo-reset` completed within the last few minutes so a single `sales_open` draw exists.
3. **Pool bootstrapped** — either
   - run `bash infrastructure/scripts/demo_rehearsal.sh` which registers 6 consumers + buys 6 tickets, then STOP the recording script before it hits `close` (recording picks up from there), OR
   - use the founder's usual `demo_close_reveal.py` seed which leaves the draw pre-populated.
4. **OBS Studio** installed (`brew install --cask obs`). One-time setup: allow Screen Recording under System Settings → Privacy & Security → Screen Recording.
5. **Chrome/Chromium** window sized to **1440 × 900** (matches `record_demo.py` viewport so the artefact is dimensionally consistent).
6. **Two tabs open** in that window:
   - Tab 1: `http://localhost:3000/login`
   - Tab 2: `http://localhost:3000/admin/draws` (blank until logged in — the login redirects here)

## Steps

### 1. OBS setup (one-off per machine)

1. Open OBS Studio.
2. New scene: "Atlas demo".
3. Add source: **Display Capture** → the display holding the Chrome window. Crop to the Chrome window bounds (`Cmd-drag` handles).
4. Settings → Output → Recording:
   - Recording Path: `~/Projects/nf_atlas/_bmad-output/demo/`
   - Recording Format: **MP4** (widely playable; WebM also fine — Playwright uses WebM natively).
   - Encoder: **Apple VT H.264 Hardware** (Apple Silicon) or **x264** (Intel).
5. Settings → Video:
   - Base (Canvas) Resolution: **1440 × 900**
   - Output (Scaled) Resolution: **1440 × 900**
   - FPS: **30**

Verify: click **Start Recording** for 5s, click **Stop Recording**, confirm the file lands in `_bmad-output/demo/`. Delete the test file.

### 2. Rehearse the click path (once, unrecorded)

Do the full path below once without recording so the muscle memory is smooth. Any hesitation or misclick shows in the final video and undermines the trust story the video is meant to sell.

### 3. Record

1. Focus the Chrome window (Tab 1: `/login`).
2. OBS → **Start Recording**.
3. **Wait 2s** — dead air at the start is fine; a jump-cut mid-action isn't.
4. **Type** the admin email: `adaobi.ibe@atlas.dev`
5. **Type** the admin password: `dev_bootstrap_password_change_me_00` (bootstrap default per `.env.example`).
6. **Click** "Sign in". Wait for `/admin` to load.
7. **Click** into the draws list (sidebar or `/admin/draws`).
8. **Click** the single active draw row → lands on `/admin/draws/[drawId]`.
9. **Pause 2s** on the detail page — the state badge, commitment hex, and lifecycle actions should be visible to the reader.
10. **Click** "Close draw" → **Click** "Yes, close draw". Wait for the state badge to flip to `sales_closed` and the "Reveal winner" button to render.
11. **Pause 2s.**
12. **Click** "Reveal winner" → **Click** "Yes, reveal winner". Wait for the winners table to render and the "View public proof →" link to appear.
13. **Pause 2s** to let the reader see the primary + reserves.
14. **Click** "View public proof →" (opens `/proof/[drawId]` in a new tab; switch to it).
15. **Scroll slowly** down the page so the reader sees: commitment → revealed inputs (server_seed, tickets_hash, bitcoin block, drand round) → winners table → verify block.
16. **Click** "Copy" on the verify command. Wait for the button to read "Copied".
17. **Pause 2s.**
18. OBS → **Stop Recording**.

### 4. Verify + rename

1. Open the produced file in QuickTime.
2. Sanity checks:
   - Full run is < 3 min (target ~90s).
   - Audio track is either absent or silent (this is a screen-only demo; leave voiceover for a separate cut).
   - Sensitive info is not on screen — no other browser tabs visible, no Slack notifications, no email preview panes.
3. Rename to the canonical path: `mv "$(ls -t _bmad-output/demo/*.mp4 | head -1)" _bmad-output/demo/atlas-hero-flow.mp4`
4. Commit only the mp4, not the raw OBS project files or any earlier takes.

## Verification

The recording is fit for purpose when:

- [ ] File exists at `_bmad-output/demo/atlas-hero-flow.mp4` (or `.webm`).
- [ ] Plays cleanly in QuickTime + a browser (`<video src>`).
- [ ] Every step in `_bmad-output/planning-artifacts/v0.5-demo-plan.md §2` from step 9 (admin login) onward is visible.
- [ ] No PII beyond the seeded superadmin email + a single primary-winner user_id hash prefix (the `/proof` page renders user_id_hash short — this is expected and safe).
- [ ] File size is bounded — a 90-second 1440×900 30fps H.264 recording should land < 20 MiB. Anything over 100 MiB means the encoder settings drifted; re-encode with `ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset veryfast output.mp4`.

## When to fall back to this runbook vs. the automated path

Prefer `infrastructure/scripts/record_demo.py` when:

- Local stack is up + healthy.
- Playwright + Chromium are installed (`infrastructure/scripts/.venv-record/bin/playwright install chromium` succeeded — under a corporate proxy this may not).
- You want a reproducible artefact CI could produce later.

Fall back to this runbook when:

- Chromium download stalled on the corporate proxy (`playwright install chromium` timed out — see [[feedback-zscaler-local-only]]).
- Colima/Docker daemon is stuck (e.g. VZ disk-lock recovery in progress).
- The presenter wants voiceover or narration overlays — OBS supports both natively; the automated script doesn't.

## Follow-ups

- The automated `infrastructure/scripts/record_demo.py` remains the canonical target; anyone with a fresh laptop (per `week-8-build-plan.md §0 ask 5` — a real second-engineer machine, not this one) should validate the automated path works end-to-end and demote this runbook to "voiceover / narration only".
- If OBS itself refuses to launch (Screen Recording permission not granted, or macOS blocks the unsigned build), fall back to QuickTime's built-in Screen Recording (Cmd-Shift-5 → Record Selected Portion). Same click path, same output naming — quality is lower but always works.