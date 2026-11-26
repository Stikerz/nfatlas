"""Skill-question module (Week 5) — UNWIRED 2026-11-26.

The skill question was removed by founder decision (AMEND-003). It was
the last of the two mechanics PRD §1 relied on to sit outside gambling
regulation; the 2026-11-23 research found no skill carve-out in the
governing State law for it to qualify for, so it was conversion friction
with no legal return — and possibly adverse, since the Lagos advertising
code may treat a "skill influences chance" claim as misleading.

Lawfulness now rests on holding a State gaming licence, not on any draw
mechanic. Do not reintroduce a question as a compliance measure without a
PRD amendment and counsel sign-off.

UNWIRED, NOT DELETED. The routes are unregistered and the service is no
longer called from the purchase path, but `skill_questions`,
`skill_question_options` and `skill_question_attempts` are RETAINED and
must not be dropped: the ADR-005 hash-chained audit log carries
`skill_question.issued` / `.answered_correct` / `.answered_wrong` events
whose `subject_id` references attempt rows. Dropping the tables orphans
chain entries.

Restoring the mechanic is code-only — no migration.
"""
