# Prize Photography — joint scoping note

**Drafted:** 2026-11-27
**Drafted by:** 🏗️ Winston (architecture) + 📋 John (scope)
**Trigger:** `design/wireframes/16-draws-carousel.md` §4.1 and the `spike/prize-photography` evaluation.
**Status:** Scoping. Nothing proposed for build until §5 is decided.

---

## 0. What the spike settled, and what it did not

**Settled:** the treatment works. A full-bleed 16:10 photograph at the head of the draw card fills the viewport, removes the dead space wireframe 16 §3.3 recorded, and resolves the "carousel of near-identical text cards reads as a spreadsheet" problem. Verified on a simulator against the live backend, both with an image and with the null fallback.

**Not settled:** everything about where the bytes come from. The spike used a nullable `prize_image_url TEXT` column and `Image.network`. That is the right shape for a spike and the wrong shape to ship.

---

## 1. 🏗️ The architecture point that reframes this

**Atlas has already decided its object storage, three times, and provisioned it zero times.**

| Consumer | Where it is specified | Status |
|---|---|---|
| KYC document + selfie images | ADR-007 §Adapters — "S3 objects carry the originals under strict access control" | Unbuilt (ADR-007 unbuilt) |
| Audit-log off-platform export | ADR-005 §Alternatives — "periodic export to off-platform storage (S3 with object-lock)" | Unbuilt |
| **Prize photography** | This note | Unbuilt |

ADR-001 §Decision already commits the substrate: *"All four [managed platforms] can host the three artefacts above plus a managed Postgres, managed Redis, and **S3-compatible storage**."* Its V0.5 amendment then records why none exists yet: *"S3 is not present in V0.5 (KYC document storage is stubbed since real KYC is deferred to Phase 3)."*

**So prize photography is not a new storage decision. It is the third caller for a facility already chosen and never stood up — and the first one with a concrete, demonstrated product reason to stand it up.** That is an argument for doing it, not against.

### 1.1 But prize images are not KYC documents, and must not share a policy

This is the design point I would not want lost:

| | KYC documents | Prize photography |
|---|---|---|
| Audience | One operator, under audit | Every visitor, logged out |
| Access | Strict, time-limited, logged | Public, cacheable, CDN-fronted |
| Contains PII | Yes — a face and an ID | No |
| Retention | Regulatory minimum/maximum (counsel Q4) | Delete when the draw archives |
| Breach impact | NDPA incident | An embarrassing photo of a car |

One bucket with one policy gets one of these wrong, and the expensive direction is making KYC documents public rather than making prize images private. **Separate buckets, separate policies, from the first line of Terraform.** Not a later refinement.

### 1.2 What the URL column gets wrong

`prize_image_url TEXT` trusts whatever is pasted into it. Three concrete failures:

1. **Availability is someone else's.** A third-party host going down takes every prize image with it, on the surface whose entire job is to make prizes feel real.
2. **No validation.** Content type, dimensions, file size, and whether the URL is even an image are all unchecked. `Image.network` on a 12 MB PNG over a Lagos 3G connection is a blank card.
3. **Mixed content and privacy.** An operator pasting an `http://` URL, or one that sets third-party cookies, is a problem the app cannot see.

**Interim position I would accept:** keep the URL column for internal demos only, with the operator pasting links to assets Atlas already controls. Do **not** put it in front of real users.

### 1.3 Sizing — the thing that bites on an Android in Lagos

The spike has no `cacheWidth`/`cacheHeight`, so a 1280×800 JPEG decodes at full resolution into a card roughly a third of that width. Across a carousel of four draws that is four full-size decodes held in memory.

The fix is derivatives, generated on upload, not fetched-then-resized:

- `card` — ~800×500, what the carousel loads
- `detail` — ~1600×1000, for the entry screen
- originals retained, never served

That is a worker job, and `atlas.outbox` already exists to trigger one.

### 1.4 Aspect ratio

Sally's point stands: cover-fit crops whatever is supplied, so prizes get beheaded. Either the operator uploads at a fixed 16:10 and the admin UI enforces it, or we build a crop step. **I would enforce the ratio and skip the cropper** — a cropper is a week of fiddly UI to avoid telling operators to supply one shape.

---

## 2. 📋 The scope point

**PRD §2 does not mention prize imagery at all.** Not in "What V1 is", not in the draw-configuration bullet, not in §3.1 mechanics. It is not a cut item either — it was simply never considered, which is how a text-only draw card got built without anyone noticing it contradicted the tone doc.

That makes this a **PRD amendment, not a defect fix**. I will not treat "the tone doc implies it" as authority to add scope.

### 2.1 Is it V1?

My position: **yes, and it is close to table stakes for the category.**

The tone doc's own Anchor 1 is BOTB, whose "core competence is making the car the emotional centre of the page". Omaze and Raffle House lead with photography too. A paid prize platform whose prizes are described only in serif text is not a restrained version of that category — it is an incomplete one.

Against that: it is **operations, not just engineering**. Somebody has to photograph a Corolla, or license images, for every single draw, forever. That is a recurring content obligation nobody has costed, and it is the part most likely to be underestimated.

### 2.2 What I am NOT proposing

- Not a media library, not multiple images per draw, not video. One image per draw.
- Not a cropper (§1.4).
- Not user-generated or winner-submitted imagery.

---

## 3. Dependency that decides the timing

**Object storage needs the managed-platform choice, which the founder deferred in the V0.5 demo-first pivot** (risk register change log, 2026-07-02). ADR-001 §Decision says the platform choice "finalised in Phase 0 … records as ADR-001 amendment".

So the honest sequence is:

```
managed-platform choice  ->  S3 provisioned  ->  upload + derivatives  ->  photography ships
        (Phase 0, deferred)       (Tobi)            (Amelia)              (operations)
```

And Phase 0 is itself now gated on the State gaming licence (delivery-framework §Phase 0, amended 2026-11-27).

**Which means prize photography is downstream of the licence.** Not because it is legally sensitive, but because it needs infrastructure that needs a platform that needs Phase 0 to close.

---

## 4. What it would cost

| | Work | Owner | Est. |
|---|---|---|---|
| A | Managed-platform choice + ADR-001 amendment | Founder + 🛡️ Tobi | gated |
| B | S3-compatible storage provisioned, **two buckets, two policies** (§1.1) | 🛡️ Tobi | 1–2d |
| C | Upload endpoint, validation, derivative worker job | 💻 Amelia | 3–4d |
| D | Admin upload UI with ratio enforcement | 💻 Amelia + 🎨 Sally | 2d |
| E | Card + entry-screen treatment, `cacheWidth`, fallback | 💻 Amelia | 1d (spiked) |
| F | PRD amendment | 📋 John | 0.5d |
| — | **Photographing the prizes** | **unowned** | **recurring** |

B and C are not prize-photography costs. They are the KYC and audit-export costs too, paid once, by whichever consumer arrives first.

---

## 5. Decisions needed from the founder

1. **Is prize photography V1 scope?** If yes, John raises the PRD amendment and it joins the Phase 1 build.
2. **Who supplies the images?** The unowned row above is the real risk. Engineering can be ready and still ship empty cards.
3. **Does S3 get provisioned for this, or wait for KYC?** My recommendation: whichever lands first pays for it — but build the two-bucket split regardless, because retrofitting a privacy boundary is how KYC documents end up public.
4. **Interim URL column — yes for internal demos, or not at all?** My recommendation: demos only, never in front of real users.

---

## 6. Recommendation

**Do it, but not yet, and not in that order.**

The spike proved the treatment is worth having. The blocker is not design or engineering — it is that Atlas has no object storage because it has no platform because Phase 0 has not closed. Building an upload flow against a bucket that does not exist is motion without progress.

**What I would do now, costing nothing:** have John raise the PRD amendment so the requirement is recorded rather than living in a wireframe footnote, and have Tobi add the two-bucket split to the platform-selection criteria so the decision is made once, correctly, when it is finally made.

**What I would not do:** ship the URL column to real users to get photography sooner. It trades a visible gap for an invisible dependency on someone else's uptime, on the surface whose job is to make prizes feel real.

— 🏗️ Winston + 📋 John
