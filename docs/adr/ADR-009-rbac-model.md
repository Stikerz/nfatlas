# ADR-009: RBAC model and permission grants

**Status:** Proposed — pending EL approval
**Date:** 2026-06-29
**Approval:** _to be signed off by Engineering Lead_
**Reversibility:** Two-way door.

## Context

`PRD.md §3.7` requires RBAC for the admin app with at minimum these roles: `operator`, `draw_admin`, `kyc_reviewer`, `finance`, `support`. The Compliance & Risk Agent requires that sensitive operator actions (KYC manual overrides, refunds, draw lifecycle transitions, prize fulfilment authorisations) are logged with the acting operator's identity.

This ADR commits the RBAC model.

## Decision

### Model

A standard **role-based** model with **permissions as the primitive** and **roles as named bundles of permissions**.

```sql
CREATE TABLE permissions (
  code        TEXT PRIMARY KEY,     -- e.g. "draw.commit", "kyc.override", "refund.issue"
  description TEXT NOT NULL,
  sensitive   BOOLEAN NOT NULL DEFAULT FALSE   -- if true, every use logs to audit_log
);

CREATE TABLE roles (
  code        TEXT PRIMARY KEY,     -- e.g. "draw_admin"
  description TEXT NOT NULL
);

CREATE TABLE role_permissions (
  role_code        TEXT NOT NULL REFERENCES roles(code),
  permission_code  TEXT NOT NULL REFERENCES permissions(code),
  PRIMARY KEY (role_code, permission_code)
);

CREATE TABLE user_roles (
  user_id    UUID NOT NULL,
  role_code  TEXT NOT NULL REFERENCES roles(code),
  granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  granted_by UUID NOT NULL,           -- user_id of the granter
  revoked_at TIMESTAMPTZ,             -- null = active
  PRIMARY KEY (user_id, role_code)
);
```

### V1 roles and permissions (initial bundle)

| Role | Permissions |
|---|---|
| `operator` | `draw.read`, `user.read`, `ticket.read`, `support.read` |
| `draw_admin` | `operator` + `draw.create`, `draw.commit`, `draw.close`, `draw.reveal`, `draw.amend_metadata` |
| `kyc_reviewer` | `operator` + `kyc.review`, `kyc.approve`, `kyc.reject`, `kyc.override` (sensitive) |
| `finance` | `operator` + `refund.issue` (sensitive), `ledger.export`, `reconciliation.run` |
| `support` | `operator` + `support.respond`, `user.contact`, `ticket.amend_owner` (sensitive) |
| `superadmin` | All permissions including `role.grant`, `role.revoke` |

### Application

- A `requires(permission_code)` decorator on every admin route checks the permission against the authenticated user's active roles.
- Sensitive permissions (`sensitive=true` in `permissions`) emit an `rbac.permission_used` event to the audit log on every use (per ADR-005), with the operator's user ID, the route, and the resource ID.
- Permission grants and revocations are themselves audit-logged (`operator.role_granted`, `operator.role_revoked`).

### Bootstrapping

A migration seeds permissions and roles per the table above. The first `superadmin` is provisioned by a one-shot bootstrap script during Phase 0 environment setup (DevSecOps runbook). Subsequent grants flow through the admin UI by an existing `superadmin`.

### Least privilege

- Operators have no default permissions beyond their named role.
- A user can hold multiple roles; effective permissions are the union.
- Engineers do not have production access by default. Production debugging requires a time-bound `superadmin` grant via the runbook, audit-logged.

### MFA enforcement

`PRD.md §3.2` requires MFA for accounts that have won a prize before claim. Extending: any user with any operator role (any role except no role) has MFA enforced at every login. Implemented in the Identity module; the RBAC check assumes valid session, so MFA gating happens before the RBAC layer.

## Alternatives considered

- **Attribute-based access control (ABAC).** Lost for V1: more flexible than needed; harder to reason about; harder for auditors to enumerate effective permissions. Revisit if operator workflows develop attribute-driven access patterns (e.g. per-region scoping in V2 multi-region).
- **Hard-coded role checks in route handlers** without a permission layer. Lost: every role change becomes a code change; new roles require redeploy. Permissions-in-DB lets new role bundles be created without code changes.
- **Group permissions by module** instead of by action. Considered: simpler but coarser. Action-level permissions let `kyc_reviewer` approve KYC without being able to override (override is a separate, sensitive permission within the same module).

## Consequences

**Positive:**
- Auditors can enumerate exactly what each role can do by querying `role_permissions`.
- Sensitive actions are unambiguous and individually audit-logged.
- New roles for V2 expansion (e.g. `marketing` for the V2 CRM module) are additive.
- MFA enforcement on all operator accounts mitigates credential-theft attacks against the most valuable accounts.

**Negative:**
- A small permission proliferation risk (one permission per sensitive action); managed by code review on permission additions.
- The `superadmin` bootstrap is a one-time risk point; mitigated by the DevSecOps runbook and post-bootstrap audit-log verification.
- Time-bound production debug grants require operator discipline; mitigated by audit-log retrospective review weekly.

**Invariants:**
- Every admin route has a `requires(...)` decorator. CI grep enforces.
- Every sensitive permission use emits an audit-log entry. Tested via Identity-module integration tests.
- No user has direct DB access in production. Enforced by DB role configuration.
