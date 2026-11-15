# Affinda Resume Parser — Round 4: Independent Confirmation & Falsification (Results)

*Evidence base: 60 new synthetic probe resumes (`R401–R460`, 10 per category), actual
Affinda responses in `affinda-round4-tests/results/round4-responses-60.json` (Sandbox
export #3, `affinda-resumes (3).json`). Scored by
`affinda-round4-tests/analyse_round4.py` against `ground_truth_round4.json`; every value
quoted here is from the real responses. Reference date for all duration/expiry
expectations: **2026-11-12**. No live API calls; no fabricated data. For each category the
analyser checks the relevant **existing** Affinda field before reporting a gap, and
separates literal text mentions from semantic claims.*

---

## 1. Executive Summary

Round 4 was designed to **confirm, narrow, or disprove** Round 3's findings on a fresh,
independent set — 60 resumes it had never seen, with explicit positive/negative controls
per category. It is a falsification pass, not a fail-hunt.

**Verdict tally across 60: 25 correct · 9 confirmed · 12 partial · 7 ambiguous ·
5 unsupported · 2 miss.**

| Area (Round-3 origin) | Probes | Round-4 outcome | Verdict vs Round 3 |
|---|---|---|---|
| **Negated skills** | R401–R410 | **7 confirmed**, 2 correct, 1 ambiguous | ✅ **CONFIRMED** — reproduces independently |
| **Skill ownership** | R411–R420 | 4 correct, 6 ambiguous | ↔ **UNCHANGED** — real but not hard-scorable |
| **Certification validity** | R421–R430 | 3 correct, 5 partial, **2 miss** | ✅ **CONFIRMED** — status lost; two certs dropped entirely |
| **Employment classification** | R431–R440 | 5 correct, 5 unsupported | ✅ **CONFIRMED + CORRECTED** (enum richer than R3 thought; still lossy) |
| **Work authorisation** | R441–R450 | 3 correct, 7 partial | ⚠️ **NARROWED** — field exists but is lossy, not "disproven" |
| **Employment duration** | R451–R460 | 8 correct, **2 confirmed** | ⚠️ **NARROWED** — robust overall, but the keyless open-ended-date bug resurfaces |

**Headline:** Round 3's strongest and most differentiated finding — **negated skills
extracted as possessed skills** — reproduced on 7 of 10 unseen cases. The two secondary
status gaps (certifications, employment classification) also held. Two Round-3 conclusions
were **refined rather than confirmed**: work authorisation is *present but lossy* (Round 3
called it "disproven"), and employment duration is *robust except for the same
open-ended-date collapse* first seen as D04 in Round 1.

---

## 2. Dataset & Methodology

60 resumes, 10 per category, each isolating one controlled variable where possible
(`ground_truth_round4.json` / `test_manifest_round4.csv`). Every category carries explicit
**positive controls** (the behaviour that *should* succeed) and **negative controls** (the
edge under test); multi-variable tests (e.g. R409 ownership + affirmation) are flagged and
scored **ambiguous** rather than attributed to one cause. Paired tests are linked via
`paired_test_id`.

Verdict scale: **correct** (handled right), **confirmed** (reproduces a real defect),
**partial** (supported field populated but lossy), **ambiguous** (defensible either way /
multi-variable), **unsupported** (the concept is not modelled by the schema), **miss** (the
entry was dropped). An open-ended value left *unknown* is acceptable — only a **fabricated**
or **misleading** value is a failure.

---

## 3. Per-Category Results (with JSON evidence)

### 3.1 Negated skills (R401–R410) — ⭐ CONFIRMED (7/10)

The parser extracts explicitly **denied** skills as possessed skills, and canonicalises
them — exactly as Round 3 found, now on new phrasings:

| Test | Source wording | Extracted (verbatim) |
|---|---|---|
| **R401** | "No hands-on experience with Kubernetes." | `Kubernetes` |
| **R402** | "Python: advanced. **Java: none**." | `Java (Programming Language)` |
| **R403** | "Experienced in AWS, **but have never used Azure**." | `Microsoft Azure` |
| **R404** | "**Theoretical knowledge** of Docker but never in production." | `Docker` |
| **R405** | "Previously used React, **but have not used it in years**." | `React` |
| **R406** | "**Without any SQL background**." | `SQL (Programming Language)` |
| **R408** | "**No experience with JavaScript.** Extensive Java…" | `JavaScript (Programming Language)` |

- **R407** ("**Not certified** in AWS, but use AWS daily") → scored **correct**: AWS *is*
  genuinely used; only the certification is denied, and that is a certification claim, not a
  skill denial.
- **R409** ("I do not manage Kubernetes clusters, but…") → **ambiguous** (negation +
  affirmation in one sentence; multi-variable).
- **R410** (positive control, all skills affirmed) → **correct**.

**Finding.** 7/7 clear negations failed identically to Round 3 (R301–R308). The denied
skill is added to the candidate's skill set — a silent false positive that surfaces the
candidate in searches they explicitly disclaimed. **Fully reproducible and independent.**

### 3.2 Skill ownership (R411–R420) — UNCHANGED (ambiguous)

4 correct (personal-skill controls R411/R414/R417/R419), 6 ambiguous. Skills belonging to
managed teams, external contractors, or "reviewed-not-written" work are attributed to the
candidate, but — as in Round 3 — over-attribution is defensible (a manager of Python
engineers has Python context) and cannot be scored a hard failure without an ownership
model. `skills[].sources` models the *section*, not *who did the work*. **Consistent with
Round 3: a genuine semantic limitation, low priority, not a clean defect.**

### 3.3 Certification validity (R421–R430) — CONFIRMED (status not preserved)

`certifications` captures `{name, date}` only — never a status. Evidence:

| Test | Source | Returned | Problem |
|---|---|---|---|
| R421 / R423 / R429 | active / renewed / active+expired pair | name + date | ✅ captured |
| **R422** | **expired** | `{name:"AWS Certified Solutions Architect", date:2022}` | reads as a valid date, not "expired" |
| **R424** | **revoked** | `{name:"Chartered Engineer licence", date:2024}` | revocation lost |
| **R428** | **suspended** | `{name:"Professional licence"}` | status lost |
| **R430** | expiry date, no validity statement | `{name:"ITIL Foundation", date:2024}` | expiry shown as a plain date |
| **R425** | **scheduled, not attempted** | `certifications: []` | **entry dropped** (miss) |
| **R426** | **attempted, failed** | `certifications: []` | **entry dropped** (miss) |

Notably R429 correctly keeps **both** an active (CISSP, 2026) and an expired (PMP, 2021)
cert — but with no field distinguishing which is which. **Confirmed, same status-loss
pattern as the education gap (CareerGuard); best shipped as a CareerGuard extension to
certifications, not a standalone product.**

### 3.4 Employment classification (R431–R440) — CONFIRMED + CORRECTED

`workExperience[].employmentType` is **richer than Round 3 reported**: Round 4 shows the
enum does include `contract` and `temporary`:

| Test | Label | `employmentType` returned | Verdict |
|---|---|---|---|
| R431 | permanent full-time | `full_time` | ✅ |
| R432 | fixed-term full-time contract | `full_time` | ✅ (full-time true) |
| R435 | paid internship | `internship` | ✅ |
| R436 | independent consulting contract | **`contract`** | ⚠️ unsupported* |
| R437 | temporary agency employment | **`temporary`** | ⚠️ unsupported* |
| **R433** | **permanent part-time** | `full_time` | ❌ part-time lost |
| **R434** | **unpaid volunteer** | `internship` | ❌ no volunteer value |
| **R438** | casual, variable hours | `part_time` | ⚠️ casual lost |

\*Marked *unsupported* because the specific working relationship (consulting vs generic
contract, agency placement, casual) is not distinctly representable, even where a nearby
enum value is emitted. **Correction to Round 3:** Round 3 (R342) saw a 6-month contract map
to `part_time` and concluded "no contract value"; Round 4 shows `contract` and `temporary`
*do* exist, so the real gap is narrower — **volunteer, part-time, casual and
agency/consulting distinctions are lossy**, not "contract is unrepresentable". An enum
extension plus consistent mapping, not a new capability.

### 3.5 Work authorisation (R441–R450) — NARROWED (present but lossy)

`workAuthorization` exists and is populated in every case (confirming Round 3 that it is
**not** an uncaptured gap), but it is a **free-text string with no structured
status/expiry/restriction**, so 7/10 are only **partial**:

| Test | Returned `workAuthorization` | Lossy because |
|---|---|---|
| R441 citizen / R444 expired / R450 conflicting | captured (R450 keeps *both* conflicting clauses) | ✅ |
| R442 | `"Australian permanent resident"` | no status enum |
| R443 | `"Authorization: Temporary work visa valid until 2028"` | **expiry 2028 not structured** |
| R445 | `"Work Authorization: Requires employer sponsorship"` | sponsorship flag only in prose |
| R447 | `"Authorization: Work rights"` | restriction (hours) dropped to a bare label |
| R449 | `"Authorization: Eligible for a visa but has not obtained one"` | eligibility≠held not distinguished |

**Narrowing of Round 3:** the field is real (so not a new field to build), but offers **no
structured expiry, restriction, or citizen/PR/visa/sponsorship enum** — a data-quality
limitation rather than a missing capability.

### 3.6 Employment duration (R451–R460) — NARROWED (robust except open-ended dates)

8/10 correct. Overlap, partial overlap, concurrent freelance, gaps, promotions, open
"Present" roles, career breaks and multi-year part-time are all handled, and
`employmentMetrics` does **not** double-count overlap (R459 `totalExperienceMonths:36`,
not 48; R460 `:60`). Two confirmed failures, both the **open-ended-date collapse**:

- **R459** (concurrent internships + university): the two 12-month internship roles each come
  back with `dateRange.end == start` (`durationMonths:12` on a zero-span date range).
- **R460** (one completed + **one unspecified end date**): the open-ended role returns
  `start 2023-01 → end 2023-01, durationMonths:12` — an open role fabricated into a fixed
  one-year stint.

**This is the same defect as D04 (Round 1) and T03/T12 (Round 2):** with no recognised
current-keyword, Affinda invents an end date equal to the start. Round 4 shows it is not
confined to the "current role" category — it also corrupts **duration** reasoning. Bounded
but cross-cutting.

---

## 4. Cross-Round Comparison

| Finding | R1 (30) | R2 (45) | R3 (48) | R4 (60) | Status |
|---|---|---|---|---|---|
| **Negated skills → extracted** | — | — | 5/5 | **7/10** | ✅ **CONFIRMED** (R3+R4) |
| **Education completion status lost** | F05 | 6/15 | — | — | ✅ CONFIRMED (R1+R2) |
| **Certification status lost** | — | — | partial | **7/10 partial+miss** | ✅ CONFIRMED (R3+R4) |
| **Employment-type enum lossy** | — | — | partial | **5/10** | ✅ CONFIRMED (scope corrected) |
| **Open-ended date → 1-month collapse** | D04 | T03/T12 | — | **R459/R460** | ✅ CONFIRMED, cross-cutting |
| **Work authorisation** | — | — | "disproven" | present-but-lossy | ⚠️ NARROWED |
| **Employer attribution (freelance bleed)** | D03 | 0/15 | — | — | ❌ NOT REPRODUCED |
| **Experience-duration double-count** | — | — | "disproven" | not reproduced (R451–R458) | ❌ NOT REPRODUCED |
| **Skill ownership over-attribution** | — | — | ambiguous | ambiguous | ↔ Real but unscored |

---

## 5. Product Implications

Round 4 does not change the recommendation hierarchy; it **hardens the evidence** behind it.

1. **Negated-/disclaimed-skill detection** — now evidenced across two independent rounds
   (12 clear failures total). The strongest, most differentiated, build-ready opportunity:
   post-extraction negation-scope detection emitting `skills[].negated` or a
   `disclaimedSkills` list. **No change: still #1.**
2. **Status enrichment (education + certifications)** — the same status-loss pattern now
   spans education (R1/R2) and certifications (R3/R4). A single **CareerGuard** enrichment
   covering `completionStatus` / `validityStatus` addresses both. Certifications fold in
   rather than needing a separate build.
3. **Open-ended-date normalisation** — upgraded in importance: it now has evidence in three
   rounds and affects both role status (D04) **and** duration metrics (R460). A
   post-extraction rule ("terminal date == start with no current-keyword → mark ongoing, do
   not fabricate an end") is low-cost and cross-cutting.
4. **Employment-type / work-authorisation structuring** — real but lower-tier: enum
   completion (volunteer/part-time/casual) and a structured work-auth sub-object
   (status/expiry/restriction). Both are field extensions, not new capabilities.

---

## 6. Limitations

- 60 **synthetic** probes, **single run** — exploratory, not production rates; consistency
  not measured.
- Sandbox schema v1.0 exposes **no per-field confidence or document warnings**; "status
  absent / unsupported" is relative to this response shape — the platform API may surface
  more.
- "Not reproduced" (employer attribution, duration double-count) means the effect did not
  appear on these controls, not that it is impossible at scale.
- Some verdicts (skill ownership, consulting-vs-contract) are **judgement calls** recorded as
  ambiguous/unsupported rather than asserted failures; no claim is made about Affinda's
  internal model or root cause.

---

*Generated from `affinda-round4-tests/results/round4-responses-60.json` via
`affinda-round4-tests/analyse_round4.py` (→ `affinda-round4-tests/findings/`). Inputs
unmodified; earlier rounds and reports untouched.*
