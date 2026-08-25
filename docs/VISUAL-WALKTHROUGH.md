# Visual walkthrough

Every Atlas surface, in the order a draw passes through them. Captured from
a running local stack — real Postgres, six registered consumers, a genuine
commit-reveal cycle. Nothing here is a mockup.

Regenerate with `infrastructure/scripts/capture_screens.py` after any UI
change; see that file's docstring for prerequisites.

## Before the draw opens

The public surface exists to be checked by someone who does not trust you. It states the free-entry route and the skill question up front rather than burying them.

### How it works

`public`

The commit-reveal protocol in plain language. Atlas is a prize competition, not a lottery — every draw carries a free entry route with identical odds, and that claim is made here.

![How it works](screens/01-how-it-works.png)


### Responsible play

`public`

Self-exclusion and spend limits. Required by the positioning, not bolted on after.

![Responsible play](screens/02-responsible-play.png)


### Public proof, before the reveal

`sealed`

The commitment — SHA-256 of the server seed and draw id — is published when the draw is created. The seed itself is withheld and encrypted at rest. Anyone can record this hash now and hold Atlas to it later.

![Public proof, before the reveal](screens/03-proof-sealed.png)


## The operator lifecycle

A draw moves through a state machine and the console offers only the actions the current state permits. The sequence below is that machine, not a tour — note how the action set changes on the same screen.

### Operator login

`auth`

Reaching `/` redirects here. Until W8 the middleware guard was never loaded — it sat one directory above the app — so `/` returned 404 and the guard did nothing.

![Operator login](screens/04-login.png)


### Dashboard

`auth`

Landing surface after sign-in.

![Dashboard](screens/05-dashboard.png)


### Draws

`index`

The operator draw index.

![Draws](screens/06-draws-list.png)


### Draw detail — sales open

`sales_open`

The commitment is shown to the operator pre-reveal, the same value the public page carries. Only **Close draw** is offered; reveal is not reachable from this state.

![Draw detail — sales open](screens/07-draw-open.png)


### Confirming an irreversible action

`sales_open`

Every lifecycle action is two-step. The copy says *this is not reversible* because it is not — a closed draw cannot reopen and a revealed one cannot be re-revealed.

![Confirming an irreversible action](screens/08-confirm.png)


### Draw detail — sales closed

`sales_closed`

State advanced, and the action set with it. Close is gone; reveal is the only move.

![Draw detail — sales closed](screens/09-draw-closed.png)


### Draw detail — revealed

`revealed`

Winners selected, draw terminal. The reveal writes an outbox row in the same transaction; the worker dispatched it in ~0.1s. The only remaining action is a link to the public proof.

![Draw detail — revealed](screens/10-draw-revealed.png)


## After the reveal

### Public proof, opened

`revealed`

The same URL as the sealed shot above, now carrying the server seed, the drand round and randomness, the tickets hash and the full winner list. The commitment published earlier still matches.

![Public proof, opened](screens/12-proof-open.png)


### Verify it yourself

`revealed`

The trust story in one control. Copy the command, run it against the published proof, recompute the winner independently — the verifier is standalone and needs nothing from Atlas.

![Verify it yourself](screens/13-verify.png)


### Hash-chained audit log

`audit`

Every event carries the hash of the one before it (ADR-005). Alter a historical row and every subsequent hash breaks, which the chain check catches on read. That is what makes the log evidence rather than a list.

![Hash-chained audit log](screens/11-audit-log.png)


## Mobile

Flutter on an iOS simulator, built from the `ios/` scaffolding added in W8 —
the platform directories had never existed, so the app could not be run at all
before then.

### Registration, on the iOS simulator

`mobile`

Fraunces display type, the +234 prefix fixed rather than a country picker, date of birth gating at 18, and terms as an explicit checkbox.

![Registration, on the iOS simulator](screens/m01-register.png)


**Six further screens are built but not pictured:** `welcome`, `otp`, `password`,
`home`, `skill_question` and `winner_claim`. All are covered by the passing widget
tests. Capturing them needs either scripted taps on the simulator, which `simctl`
cannot do, or golden files — and goldens fail because the app pulls Fraunces and
Inter from Google Fonts at runtime, which the test VM cannot reach. Wiring up
`integration_test` with bundled fonts is the fix if these need regular review.

---

Palette and type throughout are the Atlas tokens in
[`_bmad-output/planning-artifacts/design/tokens.md`](../_bmad-output/planning-artifacts/design/tokens.md)
— navy `#0F1E38`, brass `#C9A96A`, Fraunces and Inter.
