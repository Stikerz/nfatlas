# Runbook: Skill-question abuse (SEV-3 placeholder)

**Severity:** SEV-3 (SEV-2 if a real-money draw is affected)
**Owner:** on-call engineer → PM if pattern is deliberate abuse
**Last verified:** 2026-07-31 by 💻 Amelia (W5 Day 4 draft — awaiting Tobi review)
**Applies to:** V0.5 investor demo. V1 adds velocity limits + adaptive difficulty per PRD §3.5.
**Related:** week-5-build-plan.md §0 ask 2 (retry semantics), ADR-005 audit chain.

## What this runbook is (and isn't)

V0.5 intentionally ships **no anti-abuse controls** on the skill-question
surface — the mechanic is "wrong answer → new question, no penalty" per
founder decision (week-5-build-plan §0 ask 2). This runbook exists so
the first sign of abuse mid-demo does not catch on-call unprepared. It
is a placeholder for V1's real velocity checks; there is nothing to
"fix" in code from here without a scope decision.

## Symptoms

- A single user_id in the audit log with an unusually high count of
  `skill_question.issued` events over a short window.
- `skill_question.answered_wrong` events dwarfing `.answered_correct` for
  a specific user — indicating brute-forcing the pool.
- Repeated new-question requests followed by successful ticket purchase
  within a suspiciously short window — possible collusion or bot-driven
  entry.
- Support tickets from other users about "the draw entry count jumped".

## Detection

There is **no automated alert in V0.5**. Detection is manual:

```sql
-- Attempts per user in the last hour, ranked.
SELECT
  actor_id            AS user_id,
  COUNT(*) FILTER (WHERE event_name = 'skill_question.issued')             AS issued,
  COUNT(*) FILTER (WHERE event_name = 'skill_question.answered_wrong')     AS wrong,
  COUNT(*) FILTER (WHERE event_name = 'skill_question.answered_correct')   AS correct
FROM audit_log
WHERE event_name LIKE 'skill_question.%'
  AND occurred_at > now() - INTERVAL '1 hour'
GROUP BY actor_id
ORDER BY issued DESC
LIMIT 10;
```

A human user answering honestly issues maybe 2-3 questions per purchase.
Anything above ~20 issued in an hour warrants a second look.

## Impact

- **V0.5 demo:** low. Single-user demo; no real users, no real money.
- **If seen in Phase 3 live:** medium. Abuse could inflate paid entry
  count without paying — no, actually the paid entry requires a
  successful Paystack charge, so brute-forcing skill questions alone
  does not create tickets. The impact is limited to:
    - Audit-log noise (dilutes real signal in downstream analytics).
    - Potential proof point for a regulator arguing the skill test is
      trivially bypassable if the pool is too small.

## Mitigation (V0.5 — manual only)

If observed mid-demo:

1. **Do not stop the demo.** The abuse produces no material effect on
   the ticket pool or the draw output.
2. **Note the user_id** in the AI Integration Log for post-demo review.
3. **After the demo,** grep the audit log for their attempts and file a
   Phase 3 ticket describing the pattern.

There is no admin surface to lock out a user's skill-question requests
in V0.5. Do not build one ad hoc during the demo — it would touch
identity + skill + admin modules and defeats the "no anti-abuse until
V1" scope decision.

## Mitigation (V1 preview — nothing to do here yet)

Phase 3 adds:

- Per-user velocity cap on `next_question` (e.g. 10 issued / minute →
  429 with `Retry-After`).
- Pool size ≥ 100 questions so brute-force is uneconomical relative to
  ticket price.
- Adaptive difficulty: repeated correct answers do not re-shuffle to
  easier questions; repeated wrong answers can promote harder ones.
- CAPTCHA on `next_question` after N attempts in a rolling window.

Each of the above is an ADR-worthy decision when it lands (mechanic
change → prize-comp legal opinion refresh).

## Rollback steps

Nothing to roll back — no mitigation exists in V0.5 that could need
reverting.

## Post-incident actions

- AI Integration Log entry with user_id + attempt count + timing.
- If the demo is being watched by counsel or an investor when abuse is
  observed, mention it in the summary email as a known V1 gap with a
  ticketed plan.
- Re-open the "skill-question standard" conversation with Adaeze if the
  observed pattern reveals a mechanic weakness — e.g. if a naive
  brute-force always converges on a correct answer in < N attempts,
  the pool is too small.

## Notes

- V0.5's skill-question rotation is deterministic per (user, draw,
  minute) — see atlas.skill.service.next_question. Refreshing does NOT
  cycle questions faster than once per minute.
- The `skill_question_attempts` table is the audit surface; no PII in
  the payloads beyond user_id + question_id.
- Once Phase 3 lands the velocity cap, this runbook is replaced by a
  real one at SEV-2 or SEV-1 depending on the abuse volume.
