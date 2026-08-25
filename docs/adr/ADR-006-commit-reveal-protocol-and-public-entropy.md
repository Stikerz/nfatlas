# ADR-006: Commit-reveal protocol and public entropy source for draws

**Status:** Approved
**Date:** 2026-06-29
**Approved by:** S1408661 (Engineering Lead + Compliance Lead, sole founder) on 2026-07-02
**Reversibility:** One-way door once a real-money draw has run under this protocol.

## Context

`PRD.md §3.6` commits to a provably-fair draw engine: commit-reveal with CSPRNG, a public entropy source, deterministic replay, and an ordered list of winners + reserves derived from the same inputs. This ADR commits the cryptographic protocol concretely.

The trust claim is: **given the published inputs, anyone can verify the winner — and the operator could not have known the winner before sale close.**

## Decision

### Protocol stages

1. **Commit (when the draw is created):**
   - Operator generates `server_seed` = 32 cryptographically random bytes (`secrets.token_bytes(32)` on Python; FIPS-validated source on the host).
   - Operator publishes `commitment = SHA-256(server_seed || draw_id)`. The commitment is written to:
     - The draw record (`draws.commitment`).
     - The audit log (`draw.committed` event, ADR-005).
     - The public draw page on the consumer app.
   - `server_seed` is stored encrypted in Postgres (encryption key in the platform secret manager) and is **not** retrievable by any operator role until the reveal phase. The decrypt permission is granted to the worker process only.

2. **Sale (between commit and close):**
   - Users buy paid entries; postal free entries are transcribed.
   - The full ticket list grows. Entry counts (paid + free split) are public.
   - The server seed remains sealed.

3. **Close (at the scheduled close time):**
   - Sales endpoint stops accepting new tickets.
   - The full ticket list is canonicalized (sorted by `ticket_id`) and hashed: `tickets_hash = SHA-256(JCS-canonical(ticket_id_list))`.
   - `tickets_hash` is written to the draw record and audit log (`draw.entries_snapshot` event).

4. **Reveal (at the scheduled draw time, ≥ T+1 hour after close):**
   - The worker process fetches the **public entropy** for the close time:
     - `bitcoin_hash` = SHA-256 of the Bitcoin block header for the block whose timestamp is the smallest value ≥ draw close time. Source: at least two independent block explorers; values must match.
     - `drand_round` = the drand randomness for the round whose epoch >= close time. Source: the drand League of Entropy public endpoint, signature verified against the published group public key.
   - The combined entropy is `entropy = bitcoin_hash || drand_round`.
   - `server_seed` is decrypted by the worker.
   - The winner-selection function:
     ```
     prng_seed = HMAC-SHA-256(key=server_seed, msg=entropy || tickets_hash)
     # produces a deterministic stream of 32-byte blocks
     # interpret each block as a big-endian integer, modulo the ticket count
     # to produce the next selected index
     ```
     iterates to produce an ordered list of `N` distinct winning indices, where `N` = 1 primary + `K` reserves (`K` defined per draw, default 5).
   - The corresponding ticket IDs and their owners become the winner + reserves.
   - All inputs (`server_seed`, `bitcoin_hash`, `drand_round`, `tickets_hash`, the algorithm reference) are published:
     - In the audit log (`draw.revealed`, `draw.winner_selected` events).
     - On the public draw-results page.
     - Available via an `/api/v1/draws/{id}/proof` endpoint that returns the full input set.

5. **Audit / replay:**
   - A standalone verifier script (`backend/tools/verify_draw.py`) accepts a draw ID, fetches the proof, re-runs the algorithm, and returns the same winner. The script is published alongside the platform code so third parties can replay independently.

### Reserve algorithm

The deterministic stream produces winners in order. Index 0 is the primary winner; indices 1..K are reserves in declared order. If the primary winner fails KYC within the contact window or declines, reserve 1 wins. Reserves are not a separate draw — the algorithm produces the full ordered list from the same inputs (`PRD.md §3.6`).

If reserves are exhausted, the prize rolls into the next equivalent draw with full disclosure on the draw page.

### Why two entropy sources

Bitcoin block hashes and drand are independent; both are public; both have well-documented timestamps. Combining them means an attacker would need to compromise both to bias the result. drand alone has had outages; Bitcoin alone has its own (smaller) trust assumptions. The combination is more robust than either alone.

### Why HMAC-SHA-256 with `server_seed` as the key

- `server_seed` is private during the sale phase, so even an attacker who can predict the public entropy cannot predict the winner.
- After reveal, anyone with `server_seed` and the entropy can verify. HMAC is the standard primitive for "commit to a private value, prove later."

## Alternatives considered

- **NIST Randomness Beacon** as the sole public entropy source. Lost as sole source: single point of trust and a US-government dependency for an African-launched product. drand is multi-party; Bitcoin is permissionless. Combined entropy from two independent sources is stronger.
- **A trusted-randomness oracle (Chainlink VRF or similar).** Lost for V1: adds a vendor dependency and on-chain interaction overhead. Reconsider in V2 if the V1 approach faces regulatory pushback.
- **Live human-witnessed draw with no cryptographic protocol.** Lost: the long-form PRD lists this as "optional"; the V1 PRD makes the cryptographic protocol primary because it scales (witness logistics don't) and is independently verifiable. Live-streamed draws return in V2 for flagship draws above the ₦25M trigger (`delivery-framework.md §11`).
- **`server_seed` derived from the operator's HSM** instead of stored encrypted. Considered. Lost for V1: HSM operational complexity not justified at V1 scale. Encrypted-at-rest with secret-manager key meets V1 trust bar; HSM is a V2 trigger.

## Consequences

**Positive:**
- Verifiable without trust: any user, regulator, or journalist can run the verifier script and reach the same winner.
- The protocol survives operator personnel changes: no individual can predict winners ahead of reveal.
- Replayable for audits years later: all inputs persist in the audit log.

**Negative:**
- A ≥ 1-hour delay between close and draw to allow Bitcoin block confirmation and drand epoch finalisation. Acceptable; users see the close-time and draw-time as separate values on every draw page.
- Dependency on Bitcoin and drand availability. Mitigated: at least two independent block explorers per Bitcoin lookup; drand has multiple endpoints. If both sources are simultaneously unavailable, the draw is postponed (operational runbook in `docs/runbooks/draw-entropy-unavailable.md`, owned by DevSecOps).
- The `server_seed` decryption key must be tightly controlled. Mitigated: secret-manager access scoped to the worker role; rotation drilled in DevSecOps runbook.
- Anyone can verify, so any operator mistake is discoverable. Accepted — that is the point.

**Invariants:**
- A draw cannot transition to `revealed` without a valid commitment recorded.
- A draw cannot publish a winner without the proof inputs being recorded in the audit log first.
- Compliance & Risk Agent reviews every draw's proof before public announcement (`AINE-AGENTS.md §6`).
- The verifier script is published in the public repo and exercised by an integration test on every Draw Engine PR.

---

## W8 execution amendment (2026-08-24)

Stage 1's "stored encrypted in Postgres" requirement landed in Week 8 Day 1.
V0.5 had shipped `server_seed` as plaintext hex — an explicit, logged debt
(`week-5-build-plan §0 ask 5`, carried in
`docs/AI-INTEGRATION-LOG.md §Kept-in-code shortcuts`). That debt is now closed.

**What shipped:**

- `atlas.draw.crypto` — Fernet (AES-128-CBC + HMAC-SHA-256) over the 32-byte
  seed. `encrypt_server_seed` / `decrypt_server_seed` are the only entry points;
  `_fernet()` is the single place the key is unwrapped.
- Key material from `ATLAS_SERVER_SEED_KEY`, a 44-character url-safe base64
  Fernet key, per ADR-012 §V1 mechanism.
- Migration 0010 re-encrypted the legacy raw-hex row in place, so no draw
  predates the encryption.
- Verified: round-trip and tamper-rejection tests pass; the golden-vector
  primary winner is unchanged, confirming the refactor is transparent to the
  reveal algorithm; a live database check found 0 raw-hex rows.

**Two divergences from §Protocol stages 1, recorded so they are not mistaken
for delivered:**

1. **Key location.** Stage 1 says the encryption key lives in "the platform
   secret manager". It is currently an environment variable. That is the
   deliberate ADR-012 §V1 mechanism, and the Fernet token is designed to stay
   valid as the inner-layer ciphertext under a future cloud-KMS envelope
   (Phase 5). No re-encryption is required at that point.

2. **Decrypt is not worker-only.** Stage 1 says "the decrypt permission is
   granted to the worker process only" and that the seed is "not retrievable by
   any operator role until the reveal phase". In the shipped design the API
   process holds the key: `draw.service.reveal_draw` and `draw.routes.get_proof`
   both decrypt. Encryption at rest therefore protects against database-level
   disclosure — a stolen dump, a backup, a read-only DB credential — but not
   against compromise of the API process itself.

   The pre-reveal seal is enforced by the draw state machine rather than by key
   custody: `get_proof` only returns `server_seed` once the draw is `revealed`.
   That is a weaker guarantee than the ADR describes. Splitting decrypt into a
   separate process with its own key grant is V1 hardening work and needs a
   compliance review (`docs/AINE-AGENTS.md §3` lists Adaeze as a mandatory
   reviewer on Draw Engine) before it is scheduled.
