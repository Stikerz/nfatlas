# Runbook: Superadmin bootstrap

**Owner:** 🛡️ Tobi (DevSecOps) — this runbook is the authoritative reference for provisioning the first operator per ADR-009 §Bootstrapping.
**Applies to:** dev, staging, production.
**Related:** [ADR-009 RBAC model](../adr/ADR-009-rbac-model.md), [ADR-012 Secret management](../adr/ADR-012-secret-management.md), [environment-bootstrap](./environment-bootstrap.md).

---

## When to run

- **Once per environment**, before the first person needs to sign into the admin app.
- Any time the bootstrap superadmin credentials need to be rotated (script is idempotent — re-running fixes up the password + role grant).
- After a `demo-reset` in a demo environment (the DB wipe removes the seeded operator).

## Prerequisites

1. Database is up and Alembic has run to head:
   ```
   docker compose exec -T postgres pg_isready -U atlas -d atlas
   docker compose run --rm backend alembic -c migrations/alembic.ini upgrade head
   ```
2. Two env vars are set (see [`.env.example`](../../.env.example)):
   - `ATLAS_SUPERADMIN_EMAIL` — the operator's email (used as login identifier).
   - `ATLAS_SUPERADMIN_PASSWORD` — ≥ 12 characters.
3. In prod: the password is generated with `openssl rand -base64 24` and stored in the platform secret manager (per ADR-012).

## Run

```
make bootstrap
```

Or the underlying invocation:

```
docker compose run --rm backend \
    python /infrastructure/scripts/bootstrap_superadmin.py
```

## What it does

1. Opens a session against the configured database.
2. If a `users` row with the target email exists → updates password_hash + status='active' + grants the `superadmin` role (all idempotent).
3. If not → inserts a `users` row with the target email, a placeholder phone (`+2348030000000`) and DOB (`1990-01-01`), status='active', bcrypt-hashed password. Grants `superadmin`.
4. Writes an `audit_log` row: `event_name='admin.bootstrapped'`, `actor_type='system'`, `actor_id='bootstrap'`, payload includes `{user_id, email, action: 'created'|'updated'}`.
5. Prints `→ {created|updated} superadmin  id=<uuid>  email=<email>` and exits 0.

## Post-run verification (Compliance & Risk, ⚖️ Adaeze)

Per ADR-009 §Consequences: verify the audit log recorded the bootstrap.

```sql
SELECT seq, occurred_at, event_name, actor_id, payload
FROM audit_log
WHERE event_name = 'admin.bootstrapped'
ORDER BY seq DESC
LIMIT 5;
```

Confirm:
- Exactly one row per bootstrap invocation.
- `payload->>'email'` matches the intended operator.
- `prev_hash` chains cleanly (previous row's `row_hash`).

Then confirm the login path works:

1. `docker compose up -d admin` (if not running).
2. Open `http://localhost:3000/login`.
3. Sign in with the seeded credentials.
4. Land at `/admin` with the "Atlas Admin" shell and dashboard placeholder.
5. Sign out via the operator identity chip menu.
6. Confirm redirect back to `/login`.

## Rollback / lock-out recovery

If the bootstrapped operator is locked out (forgot password, or the password was never captured):

1. Set fresh `ATLAS_SUPERADMIN_PASSWORD` in the environment.
2. Re-run `make bootstrap`. The script updates the existing row.
3. The old `session.created` rows remain in the audit log; server-side sessions issued to the old password remain valid until their `expires_at` (max 8h per current config). To immediately revoke: `UPDATE sessions SET revoked_at = now() WHERE user_id = '<superadmin uuid>' AND revoked_at IS NULL;`

## Production considerations (Phase 5)

- Bootstrap runs once during environment provisioning, then the `ATLAS_SUPERADMIN_PASSWORD` env var is unset (the credential lives only in the platform secret manager pre-bootstrap).
- Post-bootstrap, subsequent operator grants happen through the admin UI (V1 — not V0.5) by an existing superadmin.
- Compliance & Risk reviews the audit-log entry within 24h of prod bootstrap; entry into `docs/compliance/reviews/` folder is Adaeze's action.
