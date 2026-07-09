# Wireframe 08 — Admin Login (and admin shell primer)

**Drafted:** 2026-07-08 (Day 8 per `tone-doc.md §8` — Week 2 begins)
**Drafted by:** 🎨 Sally (BMad UX Designer)
**Status:** Draft — pending founder review at end of Week 2.
**Covers:** Flagship flow step 8 from `v0.5-demo-plan.md §2` — *"Login — operator credential from seed."* Also introduces the admin shell (sidebar / header / content region) that every subsequent admin wireframe inherits.
**Surface:** Next.js admin — desktop-first (min viewport 1024×768; primary design target 1280×800). No mobile admin in V0.5 per plan §3 (no separate mobile admin app; the site is responsive but the design target is desktop operator use).
**Pairs with:** `tokens.md`, `tone-doc.md`, `09-create-draw.md`, and every subsequent admin wireframe 10–13.

---

## 0. Why the admin surface is different from the consumer surface

The consumer surface is designed for one person doing one thing on their phone, at aspirational moments (browsing, entering, holding a ticket, finding out they won). The admin surface is designed for one operator doing many things on a desktop, at operational moments (setting up a draw, closing sales, revealing a winner, transcribing free entries, reviewing an audit trail).

Design implications:

- **Higher information density.** A row that says one thing on the consumer draw card ("₦2,000,000 in cash") shows up on an admin table row with sale count, close time, commit hash, status chip, and inline actions. This is correct — an operator is looking at 10 things at once, not one thing at a time.
- **Same tone, different volume.** The palette, typography, spacing, radius, and elevation tokens from `tokens.md` all apply unchanged. But headline weights are lower (an admin page headline is 24pt Fraunces, not 40pt), display type is used less, and the ratio of body-to-headline content is higher.
- **The trust story remains present.** An operator's actions on this surface — creating a draw, closing sales, revealing a winner — are the actions whose auditability underpins the consumer trust story. The admin should feel like the operator *is being watched*, not because Atlas distrusts them, but because the audit is the promise. Every consequential admin action gets a written trail visible on this surface (§4 admin shell).
- **No aspiration.** No hero photography, no full-bleed, no "You're in." moments. Admin work is competent, not celebrated.

**Non-goals for V0.5:**
- **MFA on login.** Per plan §3, V0.5 has stubbed security surface. Real MFA (TOTP or SMS OTP) is a real-launch requirement — flagged in §7.
- **Password reset flow.** V0.5 has one seeded operator; no password reset UI needed. V1.
- **Session timeout UX.** V0.5 uses long-lived sessions for demo convenience. V1 needs a proper idle-timeout + re-auth flow. Flagged.
- **Multi-role RBAC.** V0.5 has two roles only (superadmin + user) per plan §3. The full 5-role RBAC per ADR-009 lands in Phase 3. Admin surface in V0.5 shows all operator functions to the seeded operator; permission checks are stubbed to "allowed".
- **Team-management surface.** V0.5 has one operator account. No "invite teammate" flow.

---

## 1. The admin shell (established here, inherited by all subsequent admin wireframes)

Every non-login admin screen sits inside this shell:

```
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                           │  ← top bar, 56pt tall
│  Atlas Admin                                    🔔 3   👤 Adaobi Ibe  ▾   │      color.surface.base
│                                                                           │      hairline bottom border
├────────────────────┬──────────────────────────────────────────────────────┤
│                    │                                                       │
│  ▪ THIS WEEK       │                                                       │
│                    │                                                       │
│  Draws        ● 1  │                                                       │
│  Tickets       247 │                                                       │
│  Claims        —   │                    < content region >                 │
│                    │                                                       │
│  ▪ OPERATE         │                    (per-wireframe layout)             │
│                    │                                                       │
│  → Draws           │                                                       │
│    Tickets         │                                                       │
│    Free entries    │                                                       │
│    Claims          │                                                       │
│                    │                                                       │
│  ▪ REVIEW          │                                                       │
│                    │                                                       │
│    Audit log       │                                                       │
│    Users           │                                                       │
│    Compliance      │                                                       │
│                    │                                                       │
│  ▪ SETTINGS        │                                                       │
│                    │                                                       │
│    Skill questions │                                                       │
│    Seed data       │                                                       │
│    (V0.5 tools)    │                                                       │
│                    │                                                       │
└────────────────────┴──────────────────────────────────────────────────────┘

Sidebar: 240pt fixed width, color.surface.elevated, hairline right border.
Content region: fluid, 24pt padding, max-width 1280pt centered.
Top bar: sticky.
```

### 1.1 Shell components (spec below)

- `AdminTopBar` — brand ("Atlas Admin", Fraunces 20pt) + notification bell (with unread count chip) + operator identity chip with dropdown (Sign out, Settings, Switch role V1).
- `AdminSidebar` — grouped nav with gold section labels ("THIS WEEK" / "OPERATE" / "REVIEW" / "SETTINGS"). Active item indicated by leading `→` arrow (not background fill — restraint over expressiveness; matches consumer surface posture).
- `NavItem` — clickable row; on hover a subtle `surface.subtle` fill; active state uses leading arrow + `text.primary` weight; inactive state uses `text.secondary`.
- `NavCounter` — small `body.small` numeric chip trailing certain nav items ("Draws ● 1" = one active draw), gold for at-a-glance status.

### 1.2 Sidebar copy inventory (used across wf-08 through wf-13)

| Group | Item | Notes |
|---|---|---|
| THIS WEEK | Draws / Tickets / Claims | Live counts, at-a-glance |
| OPERATE | Draws | Create + manage draws (wf-09, wf-11, wf-12) |
| OPERATE | Tickets | Search + inspect tickets |
| OPERATE | Free entries | Transcribe postal entries (wf-10) |
| OPERATE | Claims | Review + approve winner claims |
| REVIEW | Audit log | Chain-verified event stream (wf-13) |
| REVIEW | Users | Search users, see self-exclusion state |
| REVIEW | Compliance | Adaeze surface — reviews, risk register, copy |
| SETTINGS | Skill questions | Manage question pool (V1) |
| SETTINGS | Seed data | V0.5 tools — reset demo, load seed, spawn winner |

**"Seed data" is deliberately named "V0.5 tools"** — flags to any future reader that these controls are for a demo mode and not for real-user operation. In V1 the section is removed.

### 1.3 Notification bell

The notification bell surfaces admin events (new claim submitted, self-exclusion activated, draw closed, draw revealed). V0.5 shows a simple count chip and a dropdown list; each item deep-links to the relevant admin surface. Not covered in detail here — it's inherited by every admin screen.

### 1.4 Operator identity chip

Top-right. Composition:

```
👤 Adaobi Ibe  ▾
```

Where `Adaobi Ibe` is the operator's name (Nigerian name for the seeded operator per tone-doc.md §7 cultural context — the admin voice is Nigerian too, not generically Silicon Valley). Dropdown menu:

- Sign out
- Settings (V1)
- Help

---

## 2. Screen 8.1 — Admin login

### 2.1 Layout (min viewport 1024×768; centered card treatment)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│                                                                           │  space.2400
│                                                                           │
│                                                                           │
│                     ┌─────────────────────────────────┐                   │
│                     │                                  │                   │
│                     │   Atlas Admin                    │                   │  ← Fraunces 24pt
│                     │                                  │                   │      color.text.primary
│                     │                                  │                   │
│                     │   Sign in to operate draws,      │                   │  ← body.default, secondary
│                     │   review claims, and inspect     │                   │
│                     │   the audit log.                 │                   │
│                     │                                  │                   │
│                     │   ─────────────────────────      │                   │  ← hairline
│                     │                                  │                   │
│                     │   ▪ Email                        │                   │  ← type.label.micro
│                     │   ┌────────────────────────┐    │                   │
│                     │   │ operator@atlas.ng      │    │                   │  ← input, 48pt tall
│                     │   └────────────────────────┘    │                   │
│                     │                                  │                   │
│                     │   ▪ Password                     │                   │
│                     │   ┌────────────────────────┐    │                   │
│                     │   │ ●●●●●●●●●●●         👁 │    │                   │  ← password + show toggle
│                     │   └────────────────────────┘    │                   │
│                     │                                  │                   │
│                     │   ┌────────────────────────┐    │                   │
│                     │   │        Sign in         │    │                   │  ← primary button 52pt
│                     │   └────────────────────────┘    │                   │      full width in card
│                     │                                  │                   │
│                     │   ─────────────────────────      │                   │
│                     │                                  │                   │
│                     │   Forgot your password?          │                   │  ← inline link (V1 target;
│                     │                                  │                   │      V0.5 shows toast)
│                     └─────────────────────────────────┘                   │
│                                                                           │
│                                                                           │  space.2400
│                                                                           │
│                                                                           │
│           Atlas Africa Ltd — V0.5 demo build — 2026-07-08                 │  ← body.small, centered,
│                                                                           │      color.text.secondary
└───────────────────────────────────────────────────────────────────────────┘
```

Card: 440pt wide, `radius.large`, `elevation.1`, `surface.elevated`, 40pt padding. Centered on viewport with generous vertical padding above and below.

### 2.2 Components used

- `LoginCard` — one-off composition described above.
- `AdminBrand` — the *"Atlas Admin"* text (Fraunces 24pt). Deliberately not the consumer wordmark; the *"Admin"* suffix signals the operator surface immediately.
- `TextInput` — email and password variants (password with show/hide toggle, same as wireframe 01 §4.1).
- `Button` (primary, full width in card).
- `InlineLink` — forgot password (stub in V0.5).
- `FooterAttribution` — a small line at page bottom identifying build environment. V0.5 explicitly says *"V0.5 demo build"* + date — this is a deliberate operational cue that reduces the chance of mistakenly using the demo build for a real-user action.

### 2.3 States

**Default:** as drawn. Sign in disabled until both fields have values (no format validation on this screen — server authenticates).

**Sign in tapped (loading):** button label *"Signing in…"* + inline spinner.

**Wrong credentials:** button reverts. Banner above card: *"That combination didn't work. Try again."* — deliberately generic (no account-enumeration signal). Password field cleared; email retained. Focus returns to password.

**Rate-limited (too many attempts):** *"Too many attempts. Wait a minute before trying again."* Sign in disabled for 60s with countdown copy on the button. Rate-limit backend behaviour is Amelia + Tobi joint concern.

**Server error:** *"We couldn't sign you in. Try again in a moment."*

**MFA challenge (V1, not V0.5):** on successful password, second-factor challenge screen appears. V0.5 skips.

**Forgot-password tapped (V0.5):** toast *"Password reset arrives with V1. Contact founder for now."*

**Success:** redirect to `/admin` — the admin home / dashboard (not designed in a separate wireframe for V0.5; the initial home is *"THIS WEEK"* sidebar view expanded, showing the one active draw as a card).

### 2.4 Copy

| Element | Copy |
|---|---|
| Page brand | Atlas Admin |
| Subhead | Sign in to operate draws, review claims, and inspect the audit log. |
| Email label | Email |
| Email placeholder | operator@atlas.ng |
| Password label | Password |
| Primary CTA (default) | Sign in |
| Primary CTA (loading) | Signing in… |
| Primary CTA (rate-limited) | Wait {n}s |
| Forgot-password link | Forgot your password? |
| Forgot toast (V0.5) | Password reset arrives with V1. Contact founder for now. |
| Error — wrong credentials | That combination didn't work. Try again. |
| Error — rate-limited | Too many attempts. Wait a minute before trying again. |
| Error — server | We couldn't sign you in. Try again in a moment. |
| Footer | Atlas Africa Ltd — V0.5 demo build — {date} |

**Copy commentary:**

- *"That combination didn't work"* — deliberately generic to avoid confirming whether the email exists. Standard security posture. The tone is neutral rather than mystical ("Invalid credentials" reads as machine, "That combination didn't work" reads as human without leaking data).
- The subhead lists *"draws, claims, audit log"* — the three actions an operator will do. It orients a new operator on landing without needing a separate onboarding screen.
- The footer's *"V0.5 demo build — {date}"* is a **safety line**, not marketing. Any operator glancing at the footer knows immediately whether they're on the demo or on the (future) production build. When V1 ships, this line becomes *"Atlas Africa Ltd — build {commit_hash}"* — same pattern, real environment.

### 2.5 Accessibility

- **Focus order:** Email → Password → Show/hide toggle → Sign in → Forgot-password link.
- **First focus on mount:** email input.
- **Labels:** all fields use `<label for>` associations, never placeholder-as-label.
- **Autofill:** email `autocomplete="username email"`; password `autocomplete="current-password"`.
- **Password show/hide:** `aria-label="Show password"` / `"Hide password"`; toggle is a real `<button>` inside the input group.
- **Error announcement:** banner uses `aria-live="assertive"`; the banner is inserted above the card, not inline with a field, because both fields share the "wrong combination" state.
- **Keyboard:** Enter in either field submits if both have values.
- **Contrast:** all tokens as spec.
- **Reduce motion:** no card animation; instant render.

### 2.6 Interaction

- **On success:** hard redirect to `/admin` (Next.js server-side redirect using the session cookie). Loading spinner between login POST completion and the destination screen render is a full-screen skeleton of the admin shell (sidebar shape + top bar placeholder) — feels continuous.
- **Session storage:** Next.js session cookie, httpOnly, secure, SameSite=Lax. V0.5 session is 30 days; V1 will implement a short idle-timeout per §7.
- **Signed-in bounce:** if user visits `/admin/login` while already signed in, redirect to `/admin` immediately (no login card flash).
- **Deep-link preservation:** if a user visits `/admin/draws/123` while signed out, they land on `/admin/login` with a `?next=/admin/draws/123` param; on success they're redirected to the deep link.

---

## 3. Open questions for founder review

1. **MFA in V0.5.** Currently omitted per plan §3. If the demo showing includes any suggestion of "would this handle a real operator account" the absence of MFA becomes a visible gap. Recommend adding a *"MFA arrives with V1"* line in the sign-in card so investors don't ask. Alternative: implement TOTP MFA in V0.5 too (adds ~1 day of work). Founder call.
2. **Session length.** 30 days is convenient for demo (founder doesn't get logged out mid-showing) but reads as insecure to a security-aware investor. Alternative: 8 hours (a working day). Recommend 8 hours; the founder-demo case can just re-login if needed.
3. **Operator name — currently seeded as "Adaobi Ibe" (Nigerian, per tone-doc §7).** Confirm this is the right identity for the demo operator, or provide a preferred name.
4. **Footer copy — "V0.5 demo build" is deliberate.** Some founders prefer to remove environment markers from screens investors might see. Recommend keep — the alternative is that a badly-timed browser bookmark ends up on a real user's device and there's no easy way to tell.

---

## 4. Cross-references

- Flow source: `v0.5-demo-plan.md §2` (step 8).
- Downstream: every admin wireframe 09–13 inherits the shell established in §1.
- Tokens: `tokens.md`.
- Tone: `tone-doc.md` §7 (Nigerian cultural context — operator identity + copy voice).
- ADR-009 (RBAC): V0.5 respects a two-role simplification per plan §3; full ADR-009 RBAC lands Phase 3.
- Adaeze — flagged for review: admin shell "REVIEW → Compliance" nav item is her surface. When wf-13 (audit log) lands, that same section will need her review of what operators can see vs what they cannot.

---

🎨 *End of wireframe 08. Wireframe 09 (create draw) next — the shell established here carries over; the login is the last stand-alone admin screen without the sidebar.*
