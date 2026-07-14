"""Admin (RBAC) ORM models per ADR-009.

Permissions-as-primitive; roles are named bundles; users get roles via
`user_roles`. Effective permissions = UNION over the user's roles.

V0.5 seeds 2 roles (`superadmin`, `user`) but leaves the permissions table
empty of concrete rows — the RBAC lookup surface exists but is only used
for role-membership checks until the operator surfaces need per-permission
gates (Weeks 6+).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, PrimaryKeyConstraint, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from atlas.db import Base


class Permission(Base):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Role(Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    description: Mapped[str] = mapped_column(String, nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (PrimaryKeyConstraint("role_code", "permission_code"),)

    role_code: Mapped[str] = mapped_column(
        String, ForeignKey("roles.code", ondelete="CASCADE"), nullable=False
    )
    permission_code: Mapped[str] = mapped_column(
        String, ForeignKey("permissions.code", ondelete="CASCADE"), nullable=False
    )


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (PrimaryKeyConstraint("user_id", "role_code"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role_code: Mapped[str] = mapped_column(
        String, ForeignKey("roles.code"), nullable=False
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    granted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
