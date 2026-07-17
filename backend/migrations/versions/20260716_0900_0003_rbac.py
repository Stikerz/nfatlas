"""RBAC tables + V0.5 seed (Day 5)

Revision ID: 0003_rbac
Revises: 0002_otps_and_sessions
Create Date: 2026-07-16 09:00

Lands the four ADR-009 tables:
  permissions       code PK, description, sensitive (audit-log flag).
  roles             code PK, description.
  role_permissions  (role_code, permission_code) composite PK.
  user_roles        (user_id, role_code) composite PK + granted_at + granted_by.

V0.5 seed: 2 roles ('superadmin', 'user'). Permissions table is left empty
in V0.5 per plan §1 Out — role-membership is the only gate this week; per-
permission enforcement lands as operator surfaces need it (Weeks 6+).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0003_rbac"
down_revision: Union[str, None] = "0002_otps_and_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE permissions (
            code        TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            sensitive   BOOLEAN NOT NULL DEFAULT FALSE
        );
        """
    )
    op.execute(
        """
        CREATE TABLE roles (
            code        TEXT PRIMARY KEY,
            description TEXT NOT NULL
        );
        """
    )
    op.execute(
        """
        CREATE TABLE role_permissions (
            role_code       TEXT NOT NULL REFERENCES roles(code) ON DELETE CASCADE,
            permission_code TEXT NOT NULL REFERENCES permissions(code) ON DELETE CASCADE,
            PRIMARY KEY (role_code, permission_code)
        );
        """
    )
    op.execute(
        """
        CREATE TABLE user_roles (
            user_id     UUID NOT NULL REFERENCES users(id),
            role_code   TEXT NOT NULL REFERENCES roles(code),
            granted_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            granted_by  UUID,
            PRIMARY KEY (user_id, role_code)
        );
        """
    )
    op.execute("CREATE INDEX ix_user_roles_role_code ON user_roles (role_code);")
    op.execute(
        """
        INSERT INTO roles (code, description) VALUES
          ('superadmin', 'Full-access operator; can grant / revoke any role.'),
          ('user',       'Default role for every consumer account.');
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_roles;")
    op.execute("DROP TABLE IF EXISTS role_permissions;")
    op.execute("DROP TABLE IF EXISTS roles;")
    op.execute("DROP TABLE IF EXISTS permissions;")
