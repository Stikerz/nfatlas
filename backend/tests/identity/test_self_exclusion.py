"""Self-exclusion (ADR-010 Phase A).

Asserts the amendment's invariants:
  - an excluded user cannot obtain a ticket by ANY path, including the
    webhook, which reaches ticket.service.issue_paid without the route;
  - exclusion closes the account and revokes every live session;
  - the operation is idempotent;
  - a failed MFA challenge changes nothing;
  - there is no un-exclude path.

Phase A does NOT prevent re-registration with a different email/phone —
that needs BVN, which needs KYC. `test_phase_a_does_not_block_reregistration`
pins that limitation deliberately so nobody mistakes it for a bug, and so
the test fails loudly if Phase B ever lands without updating the copy.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.admin import service as admin_service
from atlas.audit_log.models import AuditLog
from atlas.identity import mailhog_sender, self_exclusion
from atlas.identity.models import SelfExclusion, Session, User
from atlas.skill import service as skill_service
from atlas.ticket import service as ticket_service


@pytest.fixture(autouse=True)
def _stub_mailhog(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[tuple[str, str, str]]]:
    sent: list[tuple[str, str, str]] = []

    async def _fake(*, phone_e164: str, code: str, purpose: str) -> None:
        sent.append((phone_e164, code, purpose))

    monkeypatch.setattr(mailhog_sender, "send_otp", _fake)
    yield sent


async def _register_login(
    client: AsyncClient, sent_stub: list[tuple[str, str, str]]
) -> tuple[uuid.UUID, str, str]:
    """Returns (user_id, email, bearer_token)."""
    email = f"ada-{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+2348030{uuid.uuid4().int % 1_000_000:06d}"
    r = await client.post(
        "/api/v1/users",
        json={
            "email": email,
            "phone_e164": phone,
            "date_of_birth": date(1993, 3, 12).isoformat(),
            "terms_accepted": True,
        },
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    user_id = uuid.UUID(r.json()["user_id"])
    await client.post(
        "/api/v1/otps",
        json={"user_id": str(user_id), "purpose": "registration"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    await client.post(
        "/api/v1/otps/verify",
        json={
            "user_id": str(user_id),
            "purpose": "registration",
            "code": sent_stub[-1][1],
        },
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    password = "correct horse battery staple"
    await client.post(
        f"/api/v1/users/{user_id}/password",
        json={"password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    login = await client.post(
        "/api/v1/sessions",
        json={"email": email, "password": password},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    return user_id, email, login.json()["access_token"]


async def _mfa_code(
    client: AsyncClient, user_id: uuid.UUID, sent_stub: list[tuple[str, str, str]]
) -> str:
    await client.post(
        "/api/v1/otps",
        json={"user_id": str(user_id), "purpose": "login_mfa"},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    return sent_stub[-1][1]


class TestSelfExcludeEndpoint:
    async def test_closes_account_revokes_sessions_and_records_registry(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        user_id, _, token = await _register_login(client, _stub_mailhog)
        code = await _mfa_code(client, user_id, _stub_mailhog)

        resp = await client.post(
            "/api/v1/users/me/self-exclude",
            json={"confirmation": "EXCLUDE", "otp_code": code},
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["sessions_revoked"] >= 1
        # The response must not imply guarantees Phase A cannot make.
        assert body["reversible"] is False
        assert body["cross_account_enforced"] is False

        await db_session.commit()
        row = await db_session.get(SelfExclusion, user_id)
        assert row is not None
        assert row.excluded_by == "user_self"
        assert row.bvn_hash is None  # Phase B backfills

        user = await db_session.get(User, user_id)
        assert user is not None
        await db_session.refresh(user)
        assert user.status == "closed"

        live = (
            await db_session.execute(
                select(Session).where(
                    Session.user_id == user_id, Session.revoked_at.is_(None)
                )
            )
        ).scalars().all()
        assert live == []

    async def test_revoked_session_cannot_be_reused(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        user_id, _, token = await _register_login(client, _stub_mailhog)
        code = await _mfa_code(client, user_id, _stub_mailhog)
        await client.post(
            "/api/v1/users/me/self-exclude",
            json={"confirmation": "EXCLUDE", "otp_code": code},
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )
        after = await client.get(
            "/api/v1/tickets/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert after.status_code == 401, after.text

    async def test_login_refused_after_exclusion(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        user_id, email, token = await _register_login(client, _stub_mailhog)
        code = await _mfa_code(client, user_id, _stub_mailhog)
        await client.post(
            "/api/v1/users/me/self-exclude",
            json={"confirmation": "EXCLUDE", "otp_code": code},
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )
        relogin = await client.post(
            "/api/v1/sessions",
            json={"email": email, "password": "correct horse battery staple"},
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
        assert relogin.status_code >= 400, relogin.text

    async def test_wrong_mfa_code_changes_nothing(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        user_id, _, token = await _register_login(client, _stub_mailhog)
        await _mfa_code(client, user_id, _stub_mailhog)

        resp = await client.post(
            "/api/v1/users/me/self-exclude",
            json={"confirmation": "EXCLUDE", "otp_code": "000000"},
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )
        assert resp.status_code >= 400

        await db_session.commit()
        assert await db_session.get(SelfExclusion, user_id) is None
        user = await db_session.get(User, user_id)
        assert user is not None
        await db_session.refresh(user)
        assert user.status == "active"

    async def test_confirmation_string_must_be_exact(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        user_id, _, token = await _register_login(client, _stub_mailhog)
        code = await _mfa_code(client, user_id, _stub_mailhog)
        resp = await client.post(
            "/api/v1/users/me/self-exclude",
            json={"confirmation": "exclude", "otp_code": code},
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )
        assert resp.status_code == 422, resp.text

    async def test_no_unexclude_route_exists(self, client: AsyncClient) -> None:
        """V1 exclusion is permanent — the absence of the capability IS the
        enforcement (ADR-010 amendment §Invariants added)."""
        for path in (
            "/api/v1/users/me/self-exclude/reverse",
            "/api/v1/users/me/unexclude",
        ):
            r = await client.delete(path)
            assert r.status_code in (404, 405), f"{path} -> {r.status_code}"
        r = await client.delete("/api/v1/users/me/self-exclude")
        assert r.status_code in (404, 405)


class TestServiceLayerEnforcement:
    """The binding checks. Routes are one caller; the webhook is another."""

    async def test_issue_paid_refuses_excluded_user(
        self, db_session: AsyncSession
    ) -> None:
        user = User(
            email=f"x-{uuid.uuid4().hex[:8]}@example.com",
            phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
            date_of_birth=date(1990, 1, 1),
            status="active",
        )
        db_session.add(user)
        await db_session.flush()
        await self_exclusion.exclude(db_session, user_id=user.id)
        await db_session.flush()

        with pytest.raises(ticket_service.SelfExcludedError):
            await ticket_service.issue_paid(
                db_session,
                user_id=user.id,
                draw_id=uuid.uuid4(),
                payment_intent_id=uuid.uuid4(),
                entitlement_id=uuid.uuid4(),
            )

    async def test_next_question_refuses_excluded_user(
        self, db_session: AsyncSession
    ) -> None:
        user = User(
            email=f"y-{uuid.uuid4().hex[:8]}@example.com",
            phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
            date_of_birth=date(1990, 1, 1),
            status="active",
        )
        db_session.add(user)
        await db_session.flush()
        await self_exclusion.exclude(db_session, user_id=user.id)
        await db_session.flush()

        with pytest.raises(skill_service.SelfExcludedError):
            await skill_service.next_question(
                db_session, user_id=user.id, draw_id=uuid.uuid4()
            )

    async def test_exclude_is_idempotent(self, db_session: AsyncSession) -> None:
        user = User(
            email=f"z-{uuid.uuid4().hex[:8]}@example.com",
            phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
            date_of_birth=date(1990, 1, 1),
            status="active",
        )
        db_session.add(user)
        await db_session.flush()

        first, _revoked_first = await self_exclusion.exclude(
            db_session, user_id=user.id
        )
        second, revoked_second = await self_exclusion.exclude(
            db_session, user_id=user.id
        )
        await db_session.flush()

        assert first.user_id == second.user_id
        assert first.excluded_at == second.excluded_at
        assert revoked_second == 0, "replay must not re-revoke"

        events = (
            await db_session.execute(
                select(AuditLog).where(
                    AuditLog.event_name == "self_exclusion.activated",
                    AuditLog.subject_id == str(user.id),
                )
            )
        ).scalars().all()
        assert len(events) == 1, "replay must not emit a second audit event"

    async def test_unknown_user_raises(self, db_session: AsyncSession) -> None:
        with pytest.raises(self_exclusion.UnknownUserError):
            await self_exclusion.exclude(db_session, user_id=uuid.uuid4())

    async def test_operator_exclusion_is_attributed(
        self, db_session: AsyncSession
    ) -> None:
        operator = User(
            email=f"op-{uuid.uuid4().hex[:8]}@example.com",
            phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
            date_of_birth=date(1985, 1, 1),
            status="active",
        )
        subject = User(
            email=f"sub-{uuid.uuid4().hex[:8]}@example.com",
            phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
            date_of_birth=date(1990, 1, 1),
            status="active",
        )
        db_session.add_all([operator, subject])
        await db_session.flush()

        row, _ = await self_exclusion.exclude(
            db_session,
            user_id=subject.id,
            excluded_by="operator",
            excluded_by_id=operator.id,
            reason="support request",
        )
        await db_session.flush()
        assert row.excluded_by == "operator"
        assert row.excluded_by_id == operator.id
        assert row.reason == "support request"


class TestPhaseALimits:
    async def test_phase_a_does_not_block_reregistration(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        """DELIBERATE: Phase A is account-level, not identity-level.

        An excluded user CAN open a new account with a different email and
        phone. Only BVN closes that door, and BVN needs ADR-007 (KYC).
        This test pins the limitation so it is visible rather than assumed,
        and so it fails loudly if Phase B lands — at which point the
        responsible-play copy must be updated in the same change.
        """
        user_id, _, token = await _register_login(client, _stub_mailhog)
        code = await _mfa_code(client, user_id, _stub_mailhog)
        await client.post(
            "/api/v1/users/me/self-exclude",
            json={"confirmation": "EXCLUDE", "otp_code": code},
            headers={
                "Authorization": f"Bearer {token}",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )

        new_user_id, _, new_token = await _register_login(client, _stub_mailhog)
        assert new_user_id != user_id
        assert new_token, "Phase A cannot prevent this; Phase B must"


class TestAuditTrail:
    async def test_activation_is_audited_with_phase_marker(
        self, db_session: AsyncSession
    ) -> None:
        user = User(
            email=f"a-{uuid.uuid4().hex[:8]}@example.com",
            phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
            date_of_birth=date(1990, 1, 1),
            status="active",
        )
        db_session.add(user)
        await db_session.flush()
        await self_exclusion.exclude(db_session, user_id=user.id)
        await db_session.flush()

        row = (
            await db_session.execute(
                select(AuditLog).where(
                    AuditLog.event_name == "self_exclusion.activated",
                    AuditLog.subject_id == str(user.id),
                )
            )
        ).scalar_one()
        assert row.payload["bvn_enforced"] is False
        assert row.payload["excluded_by"] == "user_self"
        assert row.subject_type == "user"


class TestAdminRegistrySurface:
    """GET /api/v1/self-exclusions — operator read-only (plan item A6)."""

    async def test_requires_superadmin(
        self,
        client: AsyncClient,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        _, _, token = await _register_login(client, _stub_mailhog)
        resp = await client.get(
            "/api/v1/self-exclusions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403, resp.text
        assert resp.json()["detail"]["code"] == "operator_role_required"

    async def test_unauthenticated_is_rejected(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/self-exclusions")
        assert resp.status_code == 401

    async def test_lists_exclusions_with_phase_marker(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        _stub_mailhog: list[tuple[str, str, str]],
    ) -> None:
        subject = User(
            email=f"listed-{uuid.uuid4().hex[:8]}@example.com",
            phone_e164=f"+2348030{uuid.uuid4().int % 1_000_000:06d}",
            date_of_birth=date(1990, 1, 1),
            status="active",
        )
        db_session.add(subject)
        await db_session.flush()
        await self_exclusion.exclude(db_session, user_id=subject.id)
        await db_session.commit()

        admin_id, _, admin_token = await _register_login(client, _stub_mailhog)
        await admin_service.grant_role(
            db_session,
            user_id=admin_id,
            role_code=admin_service.SUPERADMIN_ROLE,
        )
        await db_session.commit()

        resp = await client.get(
            "/api/v1/self-exclusions",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200, resp.text
        rows = resp.json()["items"]
        match = [r for r in rows if r["user_id"] == str(subject.id)]
        assert len(match) == 1
        assert match[0]["email"] == subject.email
        assert match[0]["excluded_by"] == "user_self"
        # Phase A rows must be distinguishable from Phase B rows.
        assert match[0]["bvn_enforced"] is False

    async def test_registry_has_no_mutation_verbs(
        self, client: AsyncClient
    ) -> None:
        """ADR-010 amendment §Invariants added: no un-exclude path exists in
        code or admin UI. Asserted here so adding one is a failing test, not
        a code-review catch."""
        for verb in ("delete", "patch", "put"):
            r = await getattr(client, verb)("/api/v1/self-exclusions")
            assert r.status_code in (404, 405), f"{verb} -> {r.status_code}"
