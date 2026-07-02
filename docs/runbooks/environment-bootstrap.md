# Runbook: Environment bootstrap (dev / staging / production)

**Severity:** Ops (not an incident runbook — an operational-setup runbook)
**Owner:** on-call engineer (human), first-time setup by DevSecOps agent + EL
**Last verified:** 2026-07-01 by 🛡️ Tobi (drafted; not yet drilled — first execution during Phase 0 environment setup)
**Applies to:** all three environments; per-environment differences flagged inline.

## Symptoms

- A new environment needs to be provisioned (Phase 0 initial setup, or a new region in V2+).
- A new engineer needs a local dev environment.
- Staging or production has been catastrophically destroyed and needs to be re-created from scratch (paired with `restore-from-backup.md`).

## Detection

- No detection — this runbook is triggered by an operational decision, not an alert.

## Impact

- If executed wrong: bootstrap produces an environment with drift from the reference config → downstream deploys fail in confusing ways, secrets get mis-scoped, RBAC is over-permissive.
- If executed right: environment is deterministic, matches the Terraform in `infrastructure/terraform/`, and can be operated by any subsequent engineer.

## Diagnosis steps

None — this runbook is a setup procedure, not a diagnosis flow.

## Mitigation steps (execution procedure)

### Prerequisites (verify before starting)

1. Node.js 20+ installed (`node --version`).
2. Docker Desktop or Docker Engine running (`docker ps`).
3. Terraform ≥ 1.6 installed (`terraform version`).
4. `gh` CLI authenticated to Atlas's GitHub org (`gh auth status`).
5. Managed-platform CLI installed and authenticated (Fly / Railway / Render / AWS CLI — final platform per ADR-001 amendment).
6. Access grants: you (the operator) have `superadmin` on the platform account for the target environment. Confirm with EL if unsure.

### For LOCAL DEV environment

1. Clone the repo: `gh repo clone <atlas-org>/nf_atlas && cd nf_atlas`.
2. Copy the env template: `cp .env.example .env.local`. (`.env.local` is gitignored.)
3. Populate `.env.local` with local-dev values only — never real vendor keys. Sandbox / test keys only.
4. Bring up the local stack: `docker compose -f infrastructure/docker/compose.yaml up -d`.
5. Verify Postgres reachable: `docker exec -it atlas-postgres psql -U atlas -c '\dt'` (expect empty schema on first bootstrap).
6. Apply migrations: `cd backend && alembic upgrade head`.
7. Run backend: `cd backend && uvicorn api.main:app --reload`.
8. In parallel terminal, run admin: `cd apps/admin && npm run dev`.
9. Verify: `curl http://localhost:8000/healthz` → `{"status":"ok"}`.

### For STAGING environment (first-time provision)

1. Confirm target managed-platform account and region — record in `docs/runbooks/environment-manifest.md`.
2. Initialise Terraform for the environment:
   ```
   cd infrastructure/terraform
   terraform init -backend-config=backends/staging.hcl
   ```
3. Review the plan carefully:
   ```
   terraform plan -var-file=envs/staging.tfvars -out=staging.tfplan
   ```
   Expected resources on first run: 1× Postgres, 1× Redis, 1× S3 bucket, 1× secrets namespace, 3× app services (backend, worker, admin), 1× DNS zone. If the plan shows anything unexpected, **stop** and escalate to EL.
4. Apply the plan:
   ```
   terraform apply staging.tfplan
   ```
5. Populate secrets. For each of the required secrets listed in `.env.example`, set via the platform CLI (do not paste into shell history — use stdin or a secret file):
   ```
   platform secrets set --env staging DATABASE_URL --from-file /tmp/db_url
   platform secrets set --env staging PAYSTACK_SECRET_KEY --from-file /tmp/paystack_sandbox
   platform secrets set --env staging KYC_VENDOR_API_KEY --from-file /tmp/kyc_sandbox
   platform secrets set --env staging SENTRY_DSN --from-file /tmp/sentry_dsn
   platform secrets set --env staging JWT_SIGNING_KEY --from-file /tmp/jwt_new_key
   platform secrets set --env staging BVN_HASH_PEPPER --from-file /tmp/bvn_pepper
   platform secrets set --env staging SERVER_SEED_ENCRYPTION_KEY --from-file /tmp/seed_enc_key
   platform secrets set --env staging WHATSAPP_BSP_TOKEN --from-file /tmp/wa_bsp
   platform secrets set --env staging S3_ACCESS_KEY --from-file /tmp/s3_key
   platform secrets set --env staging S3_SECRET_KEY --from-file /tmp/s3_secret
   ```
6. Immediately `shred` the temp files: `shred -u /tmp/*_key /tmp/*_url /tmp/*_pepper /tmp/*_dsn /tmp/*_sandbox /tmp/*_bsp /tmp/*_secret`.
7. Deploy backend + worker + admin from `main`:
   ```
   platform deploy --env staging --service backend
   platform deploy --env staging --service worker
   platform deploy --env staging --service admin
   ```
8. Run migrations against the new DB (once, via a one-off job):
   ```
   platform run --env staging --service backend -- alembic upgrade head
   ```
9. Bootstrap the first superadmin operator. Generate a strong password (`openssl rand -base64 24`); apply:
   ```
   platform run --env staging --service backend -- python -m atlas.scripts.bootstrap_superadmin --email $EL_EMAIL --password $ONE_TIME_PASSWORD
   ```
   Force password change on first login (already default behaviour).
10. Verify: `curl https://staging-api.<domain>/healthz` and `curl https://staging-api.<domain>/readyz`.
11. Log in to admin at `https://staging-admin.<domain>` and confirm superadmin session works.

### For PRODUCTION environment (first-time provision)

**Every step above for staging, with these differences:**

- Terraform backend: `backends/production.hcl`, tfvars: `envs/production.tfvars`.
- **Production secrets are LIVE keys, not sandbox.** Handle from the vendor dashboard directly to the platform secret manager — never touch a local shell.
- **Two-person rule.** All production secret writes performed with EL + one other authorised operator on a shared screen.
- The bootstrap superadmin credential is rotated to the founder's dedicated production credential within 24 hours. Log the rotation in the audit log (`docs/AI-INTEGRATION-LOG.md` and platform audit).
- Feature flag defaults to `internal-only` per `delivery-framework.md §9`. Do NOT flip the flag as part of bootstrap.

## Rollback steps

If bootstrap fails partway:

1. `terraform destroy -var-file=envs/<env>.tfvars` (only if `terraform apply` succeeded but downstream steps failed). Confirm the env name in the destroy prompt — never destroy the wrong env.
2. Revoke any secrets that were set — rotate them at the vendor side (Paystack, KYC vendor, Sentry) since they were in a partial state.
3. Delete the platform environment: `platform env destroy <env>`.
4. Re-attempt from step 1 above.

**Do NOT** attempt to hand-fix a half-bootstrapped environment. Rollback and restart is faster and safer than debugging a partial state.

## Post-incident actions

- Update `docs/runbooks/environment-manifest.md` with the new environment's identifiers (Postgres URL, Redis URL, S3 bucket, DNS records).
- Append AI Integration Log entry: `operation: created`, `artefact: <environment>`, `human_reviewer: <EL>`.
- Schedule the first backup restore drill within 7 days of environment going live (see `restore-from-backup.md`).
- Add the new environment to CI's deployment target list.
