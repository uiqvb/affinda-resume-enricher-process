# Affinda Resume Parser — Full Defect Report (per-variation)

*Every defect and near-defect found across all four test rounds, broken down to the
individual résumé line that triggered it, with pass/fail per variation so patterns are
visible. 183 synthetic resumes total (R1 = 30, R2 = 45, R3 = 48, R4 = 60). All verdicts come
from scoring the real Sandbox responses; nothing is hand-counted. Use this to judge which
issues are worth building against.*

---

## How to read the verdicts

| Verdict | Meaning |
|---|---|
| **pass / correct** | Handled correctly (incl. positive controls). |
| **FAIL / confirmed** | A clear, reproducible defect — wrong or fabricated structured value. |
| **partial** | Not wrong, but meaning (status/validity) is lost — present in text, absent from structured fields. |
| **ambiguous** | Reasonable either way, or depends on how Affinda defines the field. Not counted as a defect. |
| **unsupported** | The concept is not modelled by the schema at all. |
| **miss / dropped** | The entry was removed from structured output entirely. |
| **inconclusive / status-absent** | No false value emitted, but no structured status either. |

**Three honest buckets:** *confirmed mistake* (wrong value) · *missing information* (meaning
not structured) · *ambiguous* (judgement call). They are kept separate throughout.

---

## Summary — which areas are worth working on

| # | Defect area | Resumes | Clear fails | Partial / lossy | Pattern strength | Lean |
|---|---|:--:|:--:|:--:|---|---|
| 1 | **Negated skills** | 18 | 12 | — | **Strong, reproducible** across 2 rounds | **Build (V1)** |
| 2 | **Education completion status** | 16 | 7 | 6 absent + 1 dropped | **Strong, systematic** (0/16 status) | **Build (V1)** |
| 3 | **Certification validity** | 18 | 2 dropped (defensible) | 5 partial (+3 unsupported) | **Strong** (0/18 status) | **Build (V1, w/ education)** |
| 4 | **Open-ended employment dates** | ~17 | 5 | — | **Narrow but reproducible** (keyless only) | **Build (V1, cheap)** |
| 5 | **Employment type / classification** | 18 | — | 9 unsupported | Real, enum-level | Secondary (V2) |
| 6 | **Work authorisation** | 18 | — | 7 partial | Real but field already exists | Secondary (V2) |
| 7 | **Hidden / invisible PDF text** | 5 | — | 5/5 extracted, no warning | Consistent; integrity-not-accuracy | V2 (VisibleProof) |
| 8 | **Skill ownership** | 18 | — | 12 ambiguous | Real but **unscorable** without ownership model | Defer |
| 9 | **Employer attribution** | 16 | 1 (R1 only) | — | **Did not reproduce** (15/15 clean) | Drop |
| 10 | **Experience-duration totals** | 16 | — | — | Robust (overlap not double-counted) | Drop |

*Minor one-offs: `Q2 2021` → year precision (quarter lost, D05); PDF annotation text not
extracted (C04). Both low impact.*

---

## 1. Negated skills — 18 resumes (R301–R308, R401–R410)

**Pattern:** a clean, explicit negation (`no experience with X`, `not proficient in X`,
`but not X`, `X: none`, `without any X`) → the denied skill is extracted as possessed, often
canonicalised. **12/12 clean negations failed.** Soft/partial wording (`limited exposure`,
`previously used… no longer`) is genuinely ambiguous. Certification-only denials
(`not certified in AWS, but use AWS daily`) are correctly *not* treated as skill denials.

| ID | Résumé line (the variation) | Verdict | What happened |
|---|---|---|---|
| R301 | `Skills: Python, SQL, Docker` (positive control) | pass | all three extracted |
| R302 | `No experience with Java.` | **FAIL** | `Java` extracted as a skill |
| R303 | `Not proficient in C++.` | **FAIL** | `C++` extracted |
| R304 | `Limited exposure to Rust.` | ambiguous | partial-experience wording |
| R305 | `Expert in Python; no experience with R.` | **FAIL** | `R` extracted |
| R306 | `Familiar with AWS, but not Azure.` | **FAIL** | `Azure` extracted → "Microsoft Azure" |
| R307 | `Previously used PHP; no longer work with it.` | ambiguous | historical use |
| R308 | `Python, SQL (not Tableau).` | **FAIL** | `Tableau` extracted |
| R401 | `No hands-on experience with Kubernetes.` | **FAIL** | `Kubernetes` extracted |
| R402 | `Python: advanced. Java: none.` | **FAIL** | `Java` extracted |
| R403 | `Experienced in AWS, but have never used Azure.` | **FAIL** | `Azure` extracted |
| R404 | `Theoretical knowledge of Docker but no practical Docker experience.` | **FAIL** | `Docker` extracted |
| R405 | `Previously used React, but have not used it in five years.` | **FAIL** | `React` extracted |
| R406 | `Without any SQL background.` | **FAIL** | `SQL` extracted |
| R407 | `Not certified in AWS, but use AWS daily.` | pass | AWS legitimately used; cert≠skill denial |
| R408 | `No experience with JavaScript. Extensive Java experience.` | **FAIL** | `JavaScript` extracted |
| R409 | `I do not manage Kubernetes clusters, but develop apps deployed to Kubernetes.` | ambiguous | negation + affirmation in one line |
| R410 | `Expertise in Python, Kubernetes, SQL and Azure.` (positive control) | pass | all extracted |

**Tally:** 12 FAIL · 3 pass (2 controls + R407) · 3 ambiguous. **Reproduced independently in
R3 and R4.** Caveat: we have not confirmed Affinda *defines* its skills array as "claimed
expertise" vs "all mentions" — treat as a semantic-interpretation gap.

---

## 2. Education completion status — 16 resumes (F05, T31–T45)

**Pattern:** **0/16 produced a structured status field.** When the entry carries a terminal
year, Affinda emits it as a conferral-style end date regardless of explicit
incomplete/withdrawn/not-awarded/expected wording (incl. **future** 2027 "conferrals"). When
it says "in progress/candidate/deferred" it sets `current=true` (no false date) but still no
status. One entry was dropped entirely.

| ID | Variation | Verdict | What happened |
|---|---|---|---|
| T31 | `completed` (control) | pass | correct conferral year |
| T39 | `PhD awarded 2024` (control) | pass | correct |
| F05 | `J.D. — discontinued / INCOMPLETE, expected 2026` | **FAIL** | returned completed, `end 2026`, no status |
| T33 | `Expected graduation 2027` | **FAIL** | `end 2027` shown as a conferral (future) |
| T35 | `Master NOT completed` | **FAIL** | `end 2023` → reads as earned |
| T36 | `J.D. incomplete` | **FAIL** | `end 2023` → reads as earned |
| T37 | `J.D. expected completion 2027` | **FAIL** | `end 2027` (future conferral) |
| T40 | `withdrawn` | **FAIL** | `end 2020` → reads as earned |
| T42 | `coursework completed, qualification NOT awarded` | **FAIL** | `end 2020` → reads as awarded |
| T32 | `currently studying` | status-absent | `current=true`, no status |
| T34 | `master in progress` | status-absent | `current=true`, no status |
| T38 | `PhD candidate, research ongoing` | status-absent | `current=true`, no status |
| T41 | `deferred` | status-absent | `current=true`, no status |
| T44 | `two quals: one completed + one in progress` | status-absent | in-progress one unflagged |
| T45 | `same as T44, table layout` (paired) | status-absent | layout no effect |
| T43 | `Certificate IV — currently enrolled` | **dropped** | `education: []` (entry lost) |

**Tally:** 2 pass (controls) · 7 FAIL (misleading conferral) · 6 status-absent · 1 dropped.
**Systematic.** Highest-confidence "missing information" defect.

---

## 3. Certification validity — 18 resumes (R333–R340, R421–R430)

**Pattern:** `certifications` keeps `{name, date}` only — **0/18 carry a status.** Active/
renewed certs are captured fine. Expired/revoked/suspended keep a date that *reads as valid*.
Scheduled-but-not-taken and attempted-and-failed are often **dropped** (which can be
acceptable — they may not be held credentials).

| ID | Variation | Verdict | What happened |
|---|---|---|---|
| R333 | `AWS SA — valid through 2026` | pass | name + date |
| R421 | `AWS SA — active, valid through 2027` | pass | name + date |
| R423 | `PMP — renewed 2025 (current)` | pass | name + date |
| R429 | `CISSP — active (2026)` | pass | name + date |
| R334 | `PMP — expired 2022` | ambiguous→**lossy** | date kept, no "expired" |
| R422 | `AWS SA — expired 2022` | partial | date kept, no "expired" |
| R424 | `Chartered Engineer licence — revoked 2024` | partial | revocation lost |
| R428 | `Professional licence — temporarily suspended` | partial | status lost |
| R430 | `ITIL Foundation — expires 2024` | partial | expiry shown as plain date |
| R427 | `AWS training completed; exam never taken` | partial | odd/duplicate name, no status |
| R337 | `State license — revoked 2023` | unsupported | status not modelled |
| R338 | `AWS training completed (no certification taken)` | unsupported | not a held cert |
| R339 | `Security+ coursework completed; exam not taken` | unsupported | not a held cert |
| R335 | `CISSP — exam scheduled 2025 (pending)` | ambiguous | pending not modelled |
| R336 | `CPA exam — attempted, did not pass` | ambiguous | not held |
| R340 | `PMP — active (renewed 2024)` | pass | extracted `PMP` + date 2024; only the "active" status is lost (like all) |
| R425 | `Security+ — scheduled, not yet attempted` | **dropped** | entry absent (defensible — not a held credential) |
| R426 | `Security+ — attempted, did not pass` | **dropped** | entry absent (defensible — not a held credential) |

**Tally:** 5 pass · 5 partial · 3 unsupported · 3 ambiguous · 2 dropped (both defensible).
Every *held* cert (active/renewed/expired/revoked/suspended) is extracted with name + date;
the only consistent loss is the **status label** (0/18). Scheduled/failed exams are the only
drops, and those are reasonable. Same status-loss shape as education → **share one
"qualification status" module.**

---

## 4. Open-ended employment dates — ~17 resumes (D04, T01–T15, R456/R459/R460)

**Pattern:** with **any** recognised current-keyword Affinda is correct. With **no** keyword
(bare trailing dash, lone start date, unspecified end) it **fabricates an end date equal to
the start** → a one-month role. Narrow trigger, but 100% reproducible inside it, and it
corrupts both role status *and* duration metrics.

| ID | Variation | Verdict |
|---|---|---|
| T01 | `October 2021 – Present` | pass |
| T02 | `Oct 2021 – Current` | pass |
| T04 | `Oct 2021 to date` | pass |
| T05 | `Since October 2021` | pass |
| T06 | `2021 – Present` (year-only start) | pass |
| T07 | `Oct 2021 – Ongoing` | pass |
| T08 | `October 2021 onwards` | pass |
| T09 | `Started October 2021; currently employed` | pass |
| T10 | `October 2021 – Now` | pass |
| T11 | `October 2021 – October 2024` (completed control) | pass |
| T13 | `Oct 2021 – Present` (two-column layout) | pass |
| T14 | `Oct 2021 – Present` (table layout) | pass |
| T15 | `Oct 2021 – Present` (+ overlapping role) | pass |
| R456 | `2021 – Present` (open current) | pass |
| **D04** | `October 2021 –` (dangling dash, no keyword) | **FAIL** → end = start, 1-month role |
| **T03** | `October 2021 –` (bare dash, no keyword) | **FAIL** → end = start |
| **T12** | `October 2021` (single date only) | **FAIL** → end = start |
| **R459** | concurrent internships, no explicit end | **FAIL** → per-role end = start |
| **R460** | one completed + one unspecified end | **FAIL** → open role → fixed 1-year |

**Tally:** 14 pass · 5 FAIL (all keyless). Cheapest fix: flag end-date-equals-start with no
supporting keyword; do **not** auto-assume ongoing.

---

## 5. Employment type / classification — 18 resumes (R341–R348, R431–R440)

**Pattern:** `employmentType` exists and handles permanent/full-time/internship (and even
`contract`/`temporary`), but **part-time, volunteer, casual, consulting and agency** are
lossy or coerced. No clear "wrong value", mostly "can't represent this".

| ID | Variation | Verdict | Returned |
|---|---|---|---|
| R341 | `Full-time, permanent` | pass | `full_time` |
| R343 | `Summer Internship` | pass | `internship` |
| R348 | `Internship` | pass | `internship` |
| R431 | `Permanent, full-time` | pass | `full_time` |
| R432 | `Fixed-term 6-month full-time contract` | pass | `full_time` |
| R435 | `Paid summer internship` | pass | `internship` |
| R439 | `Permanent + volunteer (two roles)` | pass | both roles kept |
| R440 | `Contract-to-permanent conversion` | pass | handled |
| R342 | `6-month contract` | unsupported | → `part_time` (R3) |
| R344 | `Volunteer (unpaid)` | unsupported | → `internship` |
| R345 | `Freelance` | unsupported | → `self_employed` |
| R346 | `Temporary seasonal` | unsupported | lossy |
| R347 | `Consultant` | ambiguous | — |
| R433 | `Permanent, part-time` | unsupported | → `full_time` (part-time lost) |
| R434 | `Volunteer (unpaid) at a charity` | unsupported | → `internship` |
| R436 | `Independent consulting contract` | unsupported | → `contract` |
| R437 | `Temporary role via staffing agency` | unsupported | → `temporary` |
| R438 | `Casual employment, variable hours` | unsupported | → `part_time` (casual lost) |

**Tally:** 8 pass · 9 unsupported · 1 ambiguous. Enum extension, not a new capability.

---

## 6. Work authorisation — 18 resumes (R309–R316, R441–R450)

**Pattern:** a free-text `workAuthorization` field **exists and is populated** (so not a
missing field), but it carries **no structured status / expiry / restriction** — so expiry
years, sponsorship flags and hour limits sit only in prose.

| ID | Variation | Verdict | Note |
|---|---|---|---|
| R309 | `U.S. Citizen` | pass | captured |
| R310 | `Permanent Resident (Green Card)` | pass | captured |
| R311 | `Requires visa sponsorship` | pass | captured |
| R312 | `Authorised to work; no sponsorship required` | pass | captured |
| R313 | `H-1B visa (valid through 2026)` | pass | captured (expiry in text) |
| R314 | `Work authorisation expired in 2023` | pass | captured |
| R315 | `` (blank control) | pass | nothing invented |
| R441 | `Australian citizen` | pass | captured |
| R444 | `Work authorisation expired in 2023` | pass | captured |
| R450 | `Authorised… // Requires sponsorship (conflicting)` | pass | both clauses kept |
| R442 | `Australian permanent resident` | partial | no status enum |
| R443 | `Temporary work visa valid until 2028` | partial | **expiry not structured** |
| R445 | `Requires employer sponsorship` | partial | flag only in prose |
| R446 | `Does not require sponsorship` | partial | flag only in prose |
| R447 | `Work rights restricted to 24 hours/week` | partial | restriction dropped to bare label |
| R448 | `Previously authorised; current status unknown` | partial | ambiguity not captured |
| R449 | `Eligible for a visa but has not obtained one` | partial | eligible≠held not distinguished |
| R316 | `Open to relocation and flexible work` | unsupported | not actually work-auth |

**Tally:** 10 pass · 7 partial · 1 unsupported. Field exists → V2 structuring, not a V1 gap.

---

## 7. Hidden / invisible PDF text — 5 resumes (B01–B05)

**Pattern:** every hiding technique still reached `rawText` (**5/5**), never corrupted a
structured field (**0/5**), name/email stayed correct, and the quality band stayed "high" —
**no visibility/integrity warning**. This is a *trust/integrity* observation (ATS keyword-
stuffing), **not** an accuracy defect and **not** a demonstrated attack.

| ID | Technique | Result |
|---|---|---|
| B01 | White text (RGB 1,1,1) on white | marker in `rawText`, not structured |
| B02 | 0.5 pt sub-visible font | marker in `rawText`, not structured |
| B03 | Text below the CropBox (off-page) | marker in `rawText` (CropBox ignored) |
| B04 | Text under a fully opaque fill | marker in `rawText` (occluded text read) |
| B05 | Render mode 3 (invisible) | marker in `rawText`, not structured |

**Tally:** 5/5 extracted, 0/5 corruption, 0/5 warning. → **VisibleProof (V2).**

---

## 8. AI-instruction / prompt-injection — 5 resumes (C01–C05)

**Pattern:** the benign instruction marker was extracted as data (4/5) but **never obeyed**
and never reached `summary`/structured fields. **No instruction-following.** C04's text lived
in a PDF annotation and was **not extracted at all** (coverage gap, not a risk).

| ID | Placement | Result |
|---|---|---|
| C01 | Visible test section | in `rawText`, not obeyed |
| C02 | Low-contrast grey text | in `rawText`, not obeyed |
| C03 | Document footer | in `rawText`, not obeyed |
| C05 | OCG / separate layer | in `rawText`, not obeyed |
| C04 | PDF FreeText annotation | **not extracted** (annotation objects not read) |

**Tally:** 0/5 instruction-following (reassuring). C04 = minor coverage gap.

---

## 9. Skill ownership — 18 resumes (R317–R324, R411–R420)

**Pattern:** skills belonging to *managed teams / colleagues / contractors* are attributed to
the candidate. Real, but **over-attribution is defensible** and cannot be scored a hard
failure without an ownership model — **12 ambiguous, 0 confirmed.**

| ID | Variation | Verdict |
|---|---|---|
| R317 | `Built the data pipeline in Spark myself.` | pass (personal) |
| R321 | `I personally wrote the service in Go.` | pass (personal) |
| R411 | `Personally developed Python services.` | pass |
| R414 | `Personally configured Kubernetes clusters.` | pass |
| R417 | `Personally developed backend services in Go.` | pass |
| R419 | `Both personally used SQL and supervised SQL analysts.` | pass |
| R318 | `Managed a team of 5 Python engineers.` | ambiguous |
| R319 | `Led a team of data scientists using TensorFlow.` | ambiguous |
| R320 | `Oversaw a Kubernetes migration performed by the platform team.` | ambiguous |
| R322 | `My team wrote the service in Go.` | ambiguous |
| R323 | `Responsible for the Java codebase.` | ambiguous |
| R324 | `I code in Python; managed a team of Go developers.` | ambiguous |
| R412 | `Managed Python engineers without writing Python.` | ambiguous |
| R413 | `Led a team whose engineers used Kubernetes; my role was financial.` | ambiguous |
| R415 | `Coordinated work by an external Java development agency.` | ambiguous |
| R416 | `Reviewed Java pull requests without writing code.` | ambiguous |
| R418 | `Managed a Go team but explicitly never used Go.` | ambiguous |
| R420 | `Evaluated React only as a competitor technology.` | ambiguous |

**Tally:** 6 pass · 12 ambiguous · 0 confirmed. **Defer** — no clean scoring.

---

## 10. Employer attribution — 16 resumes (D03, T16–T30) — DID NOT REPRODUCE

The one R1 observation (D03: freelance role inherited the neighbouring employer) **did not
reproduce** on 15 targeted variations. **15/15 pass.** Not a basis for product work.

| ID | Variation | Verdict |
|---|---|---|
| D03 | freelance "Independent" alongside permanent (R1) | **FAIL** (1, original) |
| T16–T20 | Self-Employed / Independent / Independent Contractor / Sole Trader / no-employer | pass ×5 |
| T21–T23 | freelance alongside/above/below permanent | pass ×3 |
| T24 | two simultaneous permanent employers | pass |
| T25 | consulting with multiple clients | pass |
| T26 | self-employment as a business name | pass |
| T27 | contract through a staffing agency | pass |
| T28 | three concurrent records | pass |
| T29 / T30 | two-column vs single-column (paired) | pass ×2 |

**Tally:** 15 pass · 1 historical fail. **Drop.**

---

## 11. Experience-duration totals — 16 resumes (R325–R332, R451–R458) — ROBUST

Overlap is **not** double-counted; inflated claims are not trusted; gaps/part-time/intermittent
handled. (The only duration failures, R459/R460, are the open-ended-date bug in §4, not a
metrics error.)

| ID | Variation | Verdict |
|---|---|---|
| R325 | `"10+ years"` but dates sum to ~6 | pass |
| R326 | `Part-time (20 hrs/week)` | pass |
| R327 | two concurrent roles 2020–present | pass (83 mo, not doubled) |
| R328 | 2-year gap between roles | pass |
| R329 | `"Approximately 3 years"`, no exact dates | pass |
| R330 | `"5 years"` but dates show 3 | pass |
| R331 | `Summers 2018–2021` (intermittent) | pass |
| R332 | same dates labelled full-time | pass |
| R451 | two entirely overlapping jobs | pass (not doubled) |
| R452 | three partially overlapping jobs | pass |
| R453 | full-time + freelance weekend | pass |
| R454 | multiple short contracts with gaps | pass |
| R455 | three promotions, one employer | pass |
| R457 | explicit career break | pass |
| R458 | part-time over five years | pass |

**Tally:** 16/16 pass. **Drop** (already strong; `employmentMetrics` exists).

---

## Bottom line for prioritisation

- **Build in V1 (strong evidence, reproducible, customer-impacting):** negated skills (12
  clean fails), education status (7 fails + 6 absent, 0/16 status), certification validity
  (0/18 status, pair with education), open-ended dates (5 keyless fails, cheap).
- **V2 (real but lower-tier or integrity-not-accuracy):** employment classification (enum),
  work authorisation (structure an existing field), VisibleProof (hidden text).
- **Do not build:** skill ownership (unscorable), employer attribution (did not reproduce),
  duration totals (robust).

*Caveats: all 183 resumes are synthetic and edge-case-biased; single run per document; Sandbox
schema v1.0 (no per-field confidence). "Missing information" ≠ "incorrect extraction". See
`AFFINDA_ANALYSIS.md`, `TARGETED_ANALYSIS.md`, `ROUND3_ANALYSIS.md`, `ROUND4_ANALYSIS.md` for
full per-round methodology.*
