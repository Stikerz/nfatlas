# Week 3 Build Plan — Repo Scaffold + Identity Module

**Drafted:** 2026-07-10 (Week 3 Day 1 per `v0.5-demo-plan.md §5`)
**Drafted by:** 💻 Amelia (BMad Dev)
**Status:** **Approved 2026-07-13** — founder resolved all §11 asks; Day 1 in progress.
**Applies to:** V0.5 investor demo, first backend + first UI shells.
**Pairs with:** `v0.5-demo-plan.md`, `_bmad-output/planning-artifacts/design/{tone-doc.md, tokens.md, components.md, week-2-checkpoint.md}`, `_bmad-output/planning-artifacts/design/wireframes/{01,08}.md`, `docs/adr/ADR-{001,003,004,005,009,010,012}.md`, `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md`.

---

## 0. Founder decisions (2026-07-13)

Resolves §11 asks. Applied throughout the plan below.

| # | Ask | Decision | Impact |
|---|---|---|---|
| 1 | Module directory convention | **Python src-layout** — `backend/src/atlas/{module}/` | §3 tree + all `backend/api/*` references updated to `backend/src/atlas/*`. Backend package importable as `atlas.identity`, `atlas.audit_log`, etc. `pyproject.toml` uses `[tool.hatch.build.targets.wheel] packages = ["src/atlas"]` (or equivalent for the build backend Amelia picks Day 1 morning). |
| 2 | Flutter state management | **Riverpod** | `mobile/pubspec.yaml` pins `flutter_riverpod: ^2.5.1`. No build_runner. |
| 3 | Admin package manager | **pnpm** | `admin/package.json` + `pnpm-lock.yaml`; `corepack enable` documented in README quickstart. CI uses `pnpm/action-setup@v4`. |
| 4 | Session length | **8 hours** | JWT `exp = iat + 8h`. Session row `expires_at` matches. wf-08 §7 Q2 resolved. |
| 5 | `docker compose up` cold-start gate | **90s hard-fail, <60s aspirational** | §9 exit criteria updated. Fresh-clone drill authenticity preserved (no pre-built image push). |

Adaeze's three non-blocking §6 items (rejection copy, audit redaction, cookie attrs) still owed by Day 5.

---

## 1. Scope

**In.** Repo scaffold running under `docker compose up`; identity module end-to-end (register → OTP → password → session) exercised from both the consumer (Flutter) and admin (Next.js) shells; design tokens landed in code on both surfaces; the six primitives Week 3 needs (`Button`, `Input`, `Banner`, `Modal`, `Toast`, `Nav`) built per `components.md §20.2`; audit-log skeleton writing `user.registered` / `otp.*` / `session.*` events per ADR-005; idempotency middleware per ADR-004; ADR-012 config discipline (`config.py` reads env; nowhere else does).

**Out** (V0.5 stubs per plan §3, restated for the identity slice):
- Real SMS delivery — OTP goes to Mailhog only, addressed `+234...@sms-mock.local`.
- Real MFA on admin login (wf-08 §7 flags this).
- Password-reset flow (wf-01 §4.4 stub toast; wf-08 §2.3 stub toast).
- Social login (wf-01 §7 open Q4 — recommend keep out).
- Session timeout UX (V0.5 = 30-day session per wf-08 §7 Q2; recommend swap to 8h — asks §11).
- Full RBAC per ADR-009 (V0.5 = `superadmin` + `user` only per plan §3; `permissions` / `roles` / `role_permissions` tables land but seeded with 2 roles).
- KYC (Phase 3 per ADR-007).
- Self-exclusion enforcement in registration flow (schema per ADR-010 lands as a table + BVN-pepper-in-config in Week 4 when Ticket module wires it; register endpoint doesn't check).
- CI beyond lint + typecheck + unit tests (plan §3).

---

## 2. Day-by-day breakdown (5 working days)

Each day ends demoable to founder over Zoom in < 3 minutes.

### Day 1 (Mon 2026-07-13) — Scaffold + tokens

Land the repo shape and the design tokens as code. Nothing business yet.

- `docker-compose.yaml` with `postgres:16`, `redis:7`, `mailhog`, `backend`, `worker`, `admin`. Healthchecks on all five.
- `backend/pyproject.toml` (Python 3.13, FastAPI, SQLAlchemy 2 async, Alembic, Pydantic Settings, pytest, ruff, mypy, uvicorn).
- `backend/Dockerfile.backend` + `backend/Dockerfile.worker` — same image, different CMD (per ADR-001).
- `backend/src/atlas/main.py` (FastAPI app, `/healthz`).
- `backend/src/atlas/config.py` (Pydantic Settings; ADR-012 §Application-code conventions).
- `backend/src/atlas/db.py` (async engine, session factory).
- `backend/src/atlas/{identity,wallet,payment,ticket,draw,admin,audit_log,idempotency}/__init__.py` (empty modules — module-boundary shape declared).
- `backend/migrations/{alembic.ini, env.py, versions/}` — env wired for async URL.
- `mobile/pubspec.yaml` (Flutter 3, flutter_secure_storage, dio, riverpod — see asks §11).
- `mobile/lib/main.dart`, `mobile/lib/design/tokens/{colours.dart, typography.dart, spacing.dart, radii.dart, elevation.dart}` — generated from `tokens.md §1-5`.
- `admin/package.json` (Next.js 14, TypeScript, tailwindcss, tanstack-query — pnpm per asks §11).
- `admin/tailwind.config.ts` + `admin/src/design/tokens.css` — tokens as theme extension + CSS custom props per `tokens.md §6`.
- `Makefile` — `setup / dev / test / lint / demo-reset / clean`.
- `README.md` — 15-min-fresh-clone quickstart per plan §6.
- `.env.example` (names only; ADR-012 §Locality).
- `.github/workflows/ci.yaml` — lint + typecheck + unit (matrix: py-3.13, node-20).

**Demoable end-of-day:** `git clone && cp .env.example .env && docker compose up` produces `curl localhost:8000/healthz → {"status":"ok"}` and the admin shell renders an empty page at `localhost:3000`.

### Day 2 (Tue) — Users table + POST /users + audit log skeleton

- `backend/migrations/versions/0001_users_and_audit_log.py` — `users`, `audit_log` (per ADR-005), `idempotency_records` (per ADR-004).
- `backend/src/atlas/audit_log/writer.py` — canonical-hash + prev-hash chaining. GENESIS row on first insert. JCS canonicalization (RFC 8785) via `rfc8785` package.
- `backend/src/atlas/idempotency/middleware.py` + `dependency.py` — ADR-004 §Processing steps 1-4.
- `backend/src/atlas/identity/{models.py, service.py, routes.py, schemas.py}` — `POST /api/v1/users` with 18+ server enforcement, `Idempotency-Key` required.
- `backend/tests/identity/test_register.py` — real Postgres (per `AINE-AGENTS.md §8.6`), no mocks; covers happy path, under-18 rejection, duplicate email/phone, missing/reused idempotency key, audit-log chain integrity.
- `mobile/lib/design/components/{button.dart, input.dart}`.
- `admin/src/design/components/{Button.tsx, Input.tsx}`.

**Demoable end-of-day:** `curl -X POST http://localhost:8000/api/v1/users -H 'Idempotency-Key: {uuid}' -d '{"email":"...","phone_e164":"+2348030000000","date_of_birth":"1993-03-12","terms_accepted":true}'` returns `201 {user_id, status:"pending_verification"}`, and `SELECT * FROM audit_log` shows a `user.registered` row chained to GENESIS.

### Day 3 (Wed) — OTP + password + session

- `backend/migrations/versions/0002_otps_and_sessions.py`.
- `backend/src/atlas/identity/service.py` — OTP issue (rate-limit 1/60s + 3/h per user), OTP verify (single-use, 10-min TTL), password set (bcrypt, cost 12), session create (JWT HS256, key from Pydantic Settings). Session `exp = iat + 8h` per §0 decision 4.
- `backend/src/atlas/identity/routes.py` adds: `POST /api/v1/otps`, `POST /api/v1/otps/verify`, `POST /api/v1/users/{id}/password`, `POST /api/v1/sessions`, `POST /api/v1/sessions/current/logout`.
- `backend/src/atlas/identity/mailhog_sender.py` — sends OTP email to `+234{n}@sms-mock.local` via SMTP to `mailhog:1025`. **Smoke-test this end-of-day 1 before Day 3 depends on it (risk §10.1).**
- Audit events: `otp.issued`, `otp.verified`, `otp.verification_failed`, `user.password_set`, `session.created`, `session.revoked`.
- `backend/tests/identity/test_otp_and_session.py` — same discipline as Day 2 tests.
- `mobile/lib/design/components/{banner.dart, modal.dart, toast.dart}`.
- `admin/src/design/components/{Banner.tsx, Modal.tsx, Toast.tsx}`.

**Demoable end-of-day:** shell script that registers → issues OTP → verifies (code read from Mailhog UI at `localhost:8025`) → sets password → creates session. Full audit-log chain visible in `SELECT * FROM audit_log ORDER BY seq`.

### Day 4 (Thu) — Consumer Flutter app wired to identity end-to-end (wf-01)

- `mobile/lib/services/{api_client.dart, session.dart}` — dio client with `Idempotency-Key` interceptor, session-token storage via `flutter_secure_storage`.
- `mobile/lib/features/identity/{register_screen.dart, otp_screen.dart, password_screen.dart, welcome_screen.dart}` — one file per screen in wf-01.
- `mobile/lib/design/components/nav_bar.dart` (bottom variant; shell placeholder for home).
- `mobile/lib/features/home/home_screen.dart` (placeholder — landing after welcome).
- Manual QA: full wf-01 flow on iOS simulator + Android emulator; DOB 18+ hard-stop verified; OTP-paste from clipboard tested; secure-storage roundtrip tested (cold-start with token present skips register).

**Demoable end-of-day:** iOS sim shows empty register form → email + phone + DOB → OTP (retrieved from Mailhog by founder in separate browser tab) → password → *"You're in."* welcome (800ms) → home placeholder. Session persists across cold restart of the app.

### Day 5 (Fri) — Admin Next.js wired to identity (wf-08) + hardening

- `admin/src/lib/{api-client.ts, session.ts}` — fetch wrapper with `Idempotency-Key`, session cookie (httpOnly, secure=false in dev).
- `admin/src/app/(auth)/login/page.tsx` — wf-08 §2.1 layout.
- `admin/src/app/(admin)/layout.tsx` — shell (sidebar + top bar per wf-08 §1).
- `admin/src/app/(admin)/page.tsx` — dashboard placeholder ("THIS WEEK" empty state).
- `admin/src/design/components/{Sidebar.tsx, TopBar.tsx}`.
- `infrastructure/scripts/bootstrap_superadmin.py` — one-shot seed per ADR-009 §Bootstrapping. Reads `SUPERADMIN_EMAIL` + `SUPERADMIN_PASSWORD` from env; creates the seeded operator (`Adaobi Ibe` per wf-08 §1.4).
- `infrastructure/scripts/seed_v0_5.py` — skeleton (empty this week; populated in Weeks 4-6 as modules land).
- Fresh-clone drill on a second machine (borrowed laptop or GitHub Codespace): time from `git clone` to `docker compose up` producing both apps running. Target < 15 min per plan §6.

**Demoable end-of-week:** `git clone && make setup && docker compose up` yields (a) Flutter app that walks full register flow on sim, (b) Next.js admin that walks operator login and lands on empty dashboard, (c) audit-log table showing chain-verified events for both flows.

---

## 3. Repo scaffold shopping list (Day 1 files)

```
nf_atlas/
├── README.md                                (rewrite: fresh-clone quickstart)
├── Makefile                                 (new)
├── docker-compose.yaml                      (new)
├── .env.example                             (new — names only per ADR-012)
├── .github/workflows/ci.yaml                (new)
├── backend/
│   ├── pyproject.toml                       (hatch build; packages = ["src/atlas"])
│   ├── Dockerfile.backend
│   ├── Dockerfile.worker
│   ├── src/
│   │   └── atlas/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── config.py
│   │       ├── db.py
│   │       ├── audit_log/__init__.py
│   │       ├── identity/__init__.py
│   │       ├── wallet/__init__.py
│   │       ├── payment/__init__.py
│   │       ├── ticket/__init__.py
│   │       ├── draw/__init__.py
│   │       ├── admin/__init__.py
│   │       └── idempotency/__init__.py
│   ├── migrations/
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/                        (empty; 0001 lands Day 2)
│   └── tests/
│       └── conftest.py                      (real-Postgres fixture)
├── mobile/
│   ├── pubspec.yaml                         (flutter_riverpod ^2.5.1)
│   └── lib/
│       ├── main.dart
│       └── design/tokens/
│           ├── colours.dart
│           ├── typography.dart
│           ├── spacing.dart
│           ├── radii.dart
│           └── elevation.dart
├── admin/
│   ├── package.json                         (pnpm; corepack enable in README)
│   ├── pnpm-lock.yaml
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.mjs
│   └── src/
│       ├── app/layout.tsx
│       ├── app/page.tsx
│       └── design/tokens.css
└── infrastructure/
    ├── docker/                              (empty — Dockerfiles live per-app)
    └── scripts/                             (empty; bootstrap seed lands Day 5)
```

Existing files untouched: `docs/**`, `_bmad/**`, `_bmad-output/planning-artifacts/**`, existing `.gitignore` (extend, don't overwrite).

---

## 4. Identity module contract

### 4.1 Endpoints

| Method | Path | Idempotency | Purpose |
|---|---|---|---|
| `POST` | `/api/v1/users` | required | Register — captures email, phone, DOB (18+ enforced), terms consent. Returns `user_id` + `status=pending_verification`. |
| `POST` | `/api/v1/otps` | required | Issue OTP — `{user_id, purpose}`. Rate-limited 1/60s + 3/h per user. In V0.5 → Mailhog. |
| `POST` | `/api/v1/otps/verify` | required | Consume OTP — `{user_id, code}`. Single-use. Wrong code returns 400; 3-strike + cooldown deferred. |
| `POST` | `/api/v1/users/{id}/password` | required | Set password. Requires prior `otp.verified` for `purpose=registration`. bcrypt cost 12. Sets `status=active`. |
| `POST` | `/api/v1/sessions` | required | Login — `{email, password}`. Returns JWT (30d in V0.5, see asks §11.2). Writes `session.created`. |
| `POST` | `/api/v1/sessions/current/logout` | not required | Revoke current session. |
| `GET`  | `/api/v1/sessions/current` | n/a | Return current user + session metadata (used by both Flutter + Next.js on boot). |

### 4.2 Schema (Day 2-3 migrations)

```sql
-- 0001_users_and_audit_log.py

CREATE TABLE users (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email          CITEXT UNIQUE NOT NULL,
  phone_e164     TEXT UNIQUE NOT NULL CHECK (phone_e164 ~ '^\+234[789]\d{9}$'),
  password_hash  TEXT,                                    -- null until password step
  date_of_birth  DATE NOT NULL CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '18 years'),
  status         TEXT NOT NULL CHECK (status IN ('pending_verification','active','closed')),
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (
  seq            BIGSERIAL PRIMARY KEY,
  occurred_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  actor_type     TEXT NOT NULL,
  actor_id       TEXT,
  event_name     TEXT NOT NULL,
  subject_type   TEXT NOT NULL,
  subject_id     TEXT NOT NULL,
  payload        JSONB NOT NULL,
  prev_hash      TEXT NOT NULL,
  row_hash       TEXT NOT NULL UNIQUE
);

CREATE TABLE idempotency_records (
  key           TEXT PRIMARY KEY,
  user_id       UUID,
  endpoint      TEXT NOT NULL,
  request_hash  TEXT NOT NULL,
  response_code INT,
  response_body JSONB,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at  TIMESTAMPTZ
);
CREATE INDEX idempotency_records_created_idx ON idempotency_records (created_at);
```

```sql
-- 0002_otps_and_sessions.py

CREATE TABLE otps (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL REFERENCES users(id),
  code_hash    TEXT NOT NULL,                              -- HMAC-SHA-256(otp_pepper, code)
  channel      TEXT NOT NULL CHECK (channel IN ('mailhog','sms')),
  purpose      TEXT NOT NULL CHECK (purpose IN ('registration','login_mfa')),
  issued_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at   TIMESTAMPTZ NOT NULL,
  consumed_at  TIMESTAMPTZ,
  resend_count INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX otps_user_purpose_active_idx ON otps (user_id, purpose) WHERE consumed_at IS NULL;

CREATE TABLE sessions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(id),
  issued_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ NOT NULL,
  revoked_at  TIMESTAMPTZ,
  ip_addr     INET,
  user_agent  TEXT
);
CREATE INDEX sessions_user_active_idx ON sessions (user_id) WHERE revoked_at IS NULL;
```

Append-only enforcement on `audit_log` (trigger + role grants) per ADR-005 §Append-only enforcement lands in `0001_..._audit_log.py`.

### 4.3 Audit event shapes (payload keys)

Per ADR-005 §Schema `payload JSONB`. PII redaction assumption per ADR-007 §PII redaction (Adaeze sign-off pending — see §8):

- `user.registered` → `{ user_id, email_hash, phone_e164, dob_year, terms_accepted:true }`
- `otp.issued` → `{ user_id, otp_id, channel, purpose }`
- `otp.verified` → `{ user_id, otp_id, purpose }`
- `otp.verification_failed` → `{ user_id, otp_id, reason:"wrong_code"|"expired"|"already_consumed" }`
- `user.password_set` → `{ user_id }` (no plaintext, no hash — just the fact)
- `session.created` → `{ user_id, session_id, ip_addr, user_agent }`
- `session.revoked` → `{ user_id, session_id, revoked_by:"user"|"system" }`

`actor_type` = `"user"` for `user.*` + `session.*`; `"system"` for automated `otp.verification_failed` after a timer. `subject_type` = `"user"` throughout the identity slice.

### 4.4 Module boundary invariants (per PRD §4 + ADR-001 §Consequences)

- No SELECT / INSERT into `users`, `otps`, `sessions` from any module other than `backend/src/atlas/identity/`. CI grep enforces (rule added Day 1 in `.github/workflows/ci.yaml`).
- Every write to `audit_log` goes through `backend/src/atlas/audit_log/writer.py`. CI grep enforces (rule matches direct `audit_log` INSERT / ORM calls elsewhere).
- Every state-changing endpoint on identity requires `Idempotency-Key`. Contract test in `backend/tests/identity/test_idempotency.py`.

---

## 5. Test strategy (for Murat 🧪)

Real Postgres, no mocks per `AINE-AGENTS.md §8.6`. Test DB via a dedicated Compose service `postgres-test:5433`, per-test truncation of `users`, `otps`, `sessions`, `audit_log`, `idempotency_records` (targeted TRUNCATE + `RESTART IDENTITY CASCADE` on the `audit_log.seq`).

**Unit** (`backend/tests/unit/`):
- Age computation from DOB against fixed `today`.
- OTP code generation entropy + hashing round-trip.
- Password bcrypt round-trip.
- JCS canonicalization + row-hash chaining (audit log).
- Idempotency-key request-hash calculation.

**Integration** (`backend/tests/identity/`):
- Register happy path → audit-log row chained to GENESIS.
- Register under-18 → 400 + no user row + no audit row.
- Register duplicate email → 409 + no new user row.
- Register missing `Idempotency-Key` → 400.
- Register with reused `Idempotency-Key` + same body → returns original 201 response.
- Register with reused `Idempotency-Key` + different body → 409 Conflict.
- OTP issue + verify happy path → both audit events.
- OTP verify wrong code 5× → 5 `otp.verification_failed` events.
- OTP verify after TTL → 400 with `reason=expired`.
- Password set without prior OTP verify → 403.
- Session create + logout → both audit events, session row transitions.

**Contract** (`backend/tests/contract/`):
- OpenAPI stub validates request/response shapes for all 7 endpoints (contract test using `schemathesis` or `dredd` — Amelia picks Day 3).

**Not in Week 3:**
- E2E (Playwright) — deferred to Week 6 per plan §5.
- Load / performance — plan §3 explicit non-goal.
- Fault-injection (Postgres kill mid-transaction, Mailhog offline) — Murat's Week 6 focus.

Murat gets the story context via `_bmad-output/test-artifacts/test-design/week-3-identity.md` — Amelia drafts a stub for Murat to expand.

---

## 6. Handoffs and dependencies

### To 🛡️ Tobi

**Day 1 blocking:**
- Review `docker-compose.yaml`, `Dockerfile.backend`, `Dockerfile.worker` before I merge Day 1 PR. Health-check config, port mapping, volume config for Postgres persistence across compose restarts.
- Confirm `mailhog` service exposes `1025` (SMTP) and `8025` (HTTP UI) with credentials-free access in dev.
- Sign off `.github/workflows/ci.yaml` shape — matrix, cache config, secret handling (should be none — CI runs against ephemeral test containers).

**Day 5 blocking:**
- Fresh-clone drill on a second machine. Time it. Target < 15 min per plan §6; hard budget 20 min.

**Non-blocking, Week 4 primer:**
- Runbook stub for `docker compose up` common failures (Postgres port collision, Mailhog volume perms).

### To 🏗️ Winston

**Day 1 blocking (small):**
- ~~Confirm module directory naming: `backend/api/{module}/` OK?~~ **RESOLVED §0:** src-layout — `backend/src/atlas/{module}/`.
- Confirm authentication decorator lives in `backend/src/atlas/identity/auth.py` and is imported by other modules — this is a controlled cross-module import; is there a shared/ pattern preferred?

**Day 3 blocking:**
- Sign off OpenAPI stub for the 7 identity endpoints before I ship the shape publicly.

**Non-blocking:**
- Confirm audit-event names (`user.registered`, `otp.*`, `session.*`) are the right shape for `docs/events.md` — Winston maintains the catalogue.

### To 🎨 Sally

Expected zero. Amendments to wf-01 (DOB) and wf-07 (DOB read-only cascade) already applied and audited. Ping if any layout ambiguity surfaces during Day 4.

### To ⚖️ Adaeze

**Day 2 non-blocking (but wanted before Day 5):**
- Server-side rejection message for under-18 registration: does the API return the wireframe copy (*"You must be 18 or over to use Atlas. Contact us if there's been a mistake."*) verbatim, or a shorter machine-readable error (`{code: "under_age", message: "..."}`) that Flutter maps to the copy? Recommend the latter — separates protocol from copy.
- Audit-event payload redaction for `user.registered`: is `email_hash` (SHA-256(email)) + `dob_year` (integer year only) the right redaction level for the identity slice? Or should the audit event carry full email? (ADR-005 doesn't specify; ADR-007 §PII redaction principles suggest hash.)
- Session-cookie name + attributes (`__atlas_session`, `Secure` in prod, `HttpOnly`, `SameSite=Lax`) — any compliance preference?

---

## 7. Design-system components landing this week

Per `components.md §20.2` Week 3 primitives, both platforms:

| Primitive | Flutter | Next.js | Days |
|---|---|---|---|
| `Button` | `mobile/lib/design/components/button.dart` | `admin/src/design/components/Button.tsx` | 2 |
| `Input` | `mobile/lib/design/components/input.dart` (text, password, number, phone, date, otp variants) | `admin/src/design/components/Input.tsx` | 2 (text/password) + 3 (otp/date) + 4 (phone) |
| `Banner` | `mobile/lib/design/components/banner.dart` | `admin/src/design/components/Banner.tsx` | 3 |
| `Modal` | `mobile/lib/design/components/modal.dart` | `admin/src/design/components/Modal.tsx` | 3 |
| `Toast` | `mobile/lib/design/components/toast.dart` | `admin/src/design/components/Toast.tsx` | 3 |
| `Nav` (bottom + sidebar) | `mobile/lib/design/components/nav_bar.dart` (bottom) | `admin/src/design/components/Sidebar.tsx` + `TopBar.tsx` | 4 + 5 |

Contract per component per `components.md §3-17`. Any spec ambiguity → ping Sally.

---

## 8. Risks

Ranked by likelihood × slip-impact.

1. **Alembic-async bootstrap chore (Day 1, high likelihood, half-day slip).** First-time Alembic setup with SQLAlchemy 2 async requires specific `env.py` config (async engine, `run_migrations_online` async wrapper). *Mitigation:* budget 2h Day 1 morning; fall back to sync SQLAlchemy for migrations only if async config eats > 2h.
2. **Mailhog SMTP fragility (Day 3, medium likelihood, half-day slip).** Local SMTP configs bite. *Mitigation:* smoke-test send-to-Mailhog end of Day 1 (before identity depends on it); document the wire format in `docs/runbooks/environment-bootstrap.md`.
3. **`docker compose up` cold-start < 60s target (plan §6, high likelihood aspirational).** Five services + healthchecks + initial migration typically 90s+ on first-image-build. *Mitigation:* measure Day 1; if 60s isn't achievable without pre-built images, negotiate the gate to 90s with founder (asks §11.5).
4. **JCS canonicalization + row-hash chaining bug (Day 2, medium likelihood, full-day slip if caught late).** Getting the hash wrong on Day 2 means the entire audit log rebases on Day 3 fix. *Mitigation:* pair with Winston on the JCS implementation before Day 2 commit; add a golden-vector test (known input → known hash) as first unit test in `backend/tests/unit/test_audit_log.py`.
5. **Flutter secure-storage cross-platform quirks (Day 4, medium likelihood, quarter-day slip).** iOS Keychain vs Android EncryptedSharedPreferences behave subtly differently on cold install. *Mitigation:* test both platforms Day 4 morning; use `flutter_secure_storage` v9+ which normalises.
6. **CITEXT extension availability (Day 2, low likelihood, quarter-day slip).** Postgres `CITEXT` needs `CREATE EXTENSION citext;` — should work on standard `postgres:16` image. *Mitigation:* fall back to `LOWER(email)` unique index if the extension isn't available in the test container.
7. **Client-side idempotency-key generation ergonomics (Day 4, low likelihood, no slip).** Every mutation from Flutter needs a fresh UUID passed through dio interceptor. If the interceptor is wrong every register call is treated as a retry. *Mitigation:* explicit interceptor test in `mobile/test/api_client_test.dart`.

Not a Week 3 risk but a Week 4 blocker to name early: the Wallet & Ledger module (Week 4) depends on the audit-log writer, which lands Day 2 this week. Any Day-2 audit-log bug pushes into Week 4.

---

## 9. Success gates (Week 3 exit criteria — for founder sign-off Fri EOD)

Match `v0.5-demo-plan.md §6` where applicable:

- [ ] `docker compose up` starts everything (backend, worker, admin, postgres, redis, mailhog) with healthchecks passing.
- [ ] Cold-start time measured and reported. **Hard-fail at 90s; <60s aspirational** per §0 decision 5.
- [ ] `make demo-reset` wipes and reseeds the identity slice in < 30s.
- [ ] Fresh-clone works on a second machine in < 15 min (plan §6 gate).
- [ ] Full wf-01 flow runs end-to-end on iOS simulator: register → OTP (via Mailhog) → password → welcome → home placeholder. Session persists across cold-restart.
- [ ] Full wf-08 flow runs end-to-end in Chrome: admin login → dashboard placeholder.
- [ ] `SELECT count(*) FROM audit_log` for a fresh register-through-login flow returns ≥ 5 chained rows (register + otp.issued + otp.verified + password_set + session.created), each chaining to the previous.
- [ ] CI green on PR: lint (ruff + eslint) + typecheck (mypy + tsc) + unit tests pass.
- [ ] `docs/AI-INTEGRATION-LOG.md` has entries for Days 1-5 per AINE-AGENTS §7.

---

## 10. Cross-week dependencies (Week 3 → Week 4+)

What Week 3 leaves in place for downstream weeks:

- Audit-log writer (Week 4 wallet + payment modules use it).
- Idempotency middleware (every module after this uses it).
- Design tokens + first 6 primitives (Weeks 4-7 build on them).
- Module-boundary shape (`backend/src/atlas/{six modules}/`) — Week 4 populates `wallet/` + `payment/`.
- Session middleware + `GET /sessions/current` (every authenticated call after this depends on it).
- `bootstrap_superadmin.py` (needed to test any admin surface Week 4+).

What Week 3 explicitly leaves for later:

- Real KYC (Phase 3 per ADR-007).
- Self-exclusion enforcement in the register endpoint (schema lands Week 4 with Wallet; enforcement wires Week 5 with Ticket).
- Password reset (V1).
- MFA (V1).
- Session refresh + rotation (V1).

---

## 11. Asks to founder before Day 1 code starts

**All 5 resolved 2026-07-13 — see §0.** Preserved below as the historical record of what Amelia asked and what founder decided.

1. **Module directory convention.** Recommend `backend/api/{module}/`. Alternative: `backend/src/atlas/{module}/`. → **Chose src-layout** ("the pythonic way").
2. **Flutter state management.** Recommend Riverpod. Alternative: Bloc. → **Riverpod**.
3. **Admin package manager.** Recommend pnpm. Alternative: npm. → **pnpm**.
4. **Session length.** Recommend 8h. → **8h**.
5. **60s cold-start gate.** Recommend 90s hard + <60s aspirational. → **90s hard, <60s aspirational**.

Adaeze's three non-blocking items in §6 (rejection copy, audit redaction, cookie attrs) still owed by Day 5.

---

## 12. Cross-references

- `v0.5-demo-plan.md` §2 (flagship flow), §3 (V0.5 non-goals), §5 Week 3 (assignment), §6 (success gates).
- `_bmad-output/planning-artifacts/design/week-2-checkpoint.md` §5 (handoff), §5.1 (contract points I owe), §5.2 (Day 1).
- `_bmad-output/planning-artifacts/design/{tone-doc.md, tokens.md, components.md}`.
- `_bmad-output/planning-artifacts/design/wireframes/01-register-otp-login.md` (with 2026-07-08 amendment).
- `_bmad-output/planning-artifacts/design/wireframes/08-admin-login.md`.
- `docs/adr/ADR-001` (topology + V0.5 addendum), `ADR-003` (money integer discipline — not this week but touched by audit writer), `ADR-004` (idempotency), `ADR-005` (audit log), `ADR-009` (RBAC), `ADR-010` (self-exclusion schema — not enforced this week), `ADR-012` (secrets + config.py convention).
- `docs/compliance/reviews/REVIEW-001-v0.5-consumer-wireframes.md` §5.1 (DOB at register), §7 (Amelia contract points).
- `docs/AINE-AGENTS.md` §4 (artefact registry), §8.6 (real-Postgres no-mocks discipline).

---

💻 *End of Week 3 build plan. Awaiting sign-off on §11 (5 asks) to start Day 1 Monday.*
