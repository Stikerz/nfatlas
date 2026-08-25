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

Every consumer screen, rendered from
`mobile/test/design/screen_goldens_test.dart`. These are golden files, so a UI
change shows up as an image diff in the pull request that caused it. Refresh
them with:

```bash
cd mobile && flutter test test/design/screen_goldens_test.dart --update-goldens
```

They render real typography because the faces are bundled under
`mobile/assets/google_fonts/` rather than fetched at runtime.

### Register

The +234 prefix is fixed rather than a country picker, date of birth gates at 18, and terms are an explicit checkbox.

![Register](../mobile/test/design/goldens/register.png)


### One-time code

Delivered to Mailhog in V0.5 rather than by SMS.

![One-time code](../mobile/test/design/goldens/otp.png)


### Set a password

Two rules gate the button — ten characters and a letter/number mix. The third line is advisory and always passes.

![Set a password](../mobile/test/design/goldens/password.png)


### Welcome

Auto-advances to Home after 800ms, which is why its golden is captured at 300ms.

![Welcome](../mobile/test/design/goldens/welcome.png)


### Home

Wallet chip, the active draw, and the commitment shown to the consumer before the reveal — the same hash the public proof page publishes.

![Home](../mobile/test/design/goldens/home.png)


### Skill question

Mandatory on every paid entry. This is the mechanism that makes Atlas a prize competition rather than a lottery.

![Skill question](../mobile/test/design/goldens/skill-question.png)


### Winner claim

Post-reveal claim surface.

![Winner claim](../mobile/test/design/goldens/winner-claim.png)


### Running on an iOS simulator

`simulator`

The real app on a device, device chrome and all — proof it runs, not just that its widgets paint.

![Running on an iOS simulator](screens/m01-register.png)


---

Palette and type throughout are the Atlas tokens in
[`_bmad-output/planning-artifacts/design/tokens.md`](../_bmad-output/planning-artifacts/design/tokens.md)
— navy `#0F1E38`, brass `#C9A96A`, Fraunces and Inter.
