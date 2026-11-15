# Affinda Resume Parser — Round 3 Gap Discovery (Results)

*Evidence base: 48 controlled probe resumes (`R301–R348`), actual Affinda responses in
`affinda-responses/round-3/round3-responses-48.json`. Scored by
`affinda-round3-tests/analyse_round3_results.py` against `ground_truth_round3.json`; every
value quoted is from the real responses. No live API calls; no fabricated data. Each
hypothesis was checked against the relevant EXISTING Affinda field before any gap was
claimed.*

---

## 1. Executive Summary

Round 3 probed six **new** areas (deliberately avoiding the two existing ideas —
hidden-text integrity / *VisibleProof*, and education-status + employment-date
verification / *CareerGuard*). Verdicts across 48: **22 correct · 5 confirmed failures ·
12 ambiguous · 8 unsupported-by-schema · 1 miss.**

The result is sharply focused:

| Area | Outcome |
|---|---|
| **Negated skills** | ⭐ **Confirmed, systematic (5/5).** Explicitly denied skills are extracted as possessed skills. The single strong new finding. |
| Work authorisation | **Disproven.** Affinda already has a `workAuthorization` field. |
| Experience duration | **Disproven.** `employmentMetrics` exists and did **not** double-count overlap. |
| Employment type | **Partial.** `employmentType` exists but the enum is incomplete (contract→`part_time`, volunteer→`internship`). |
| Certification status | **Real but overlaps CareerGuard.** `certifications` captures name+date, not status (expired/revoked/not-awarded lost). |
| Skill ownership | **Real but ambiguous.** Skills of *managed* people are attributed to the candidate; hard to score or fix without an ownership model. |

**The one genuinely new, strong, buildable opportunity is negated-skill detection** — the
parser treats "No experience with Java" as evidence *of* Java. It is reproducible (5/5),
customer-impacting (candidates matched to skills they explicitly disclaimed), differentiated
(no existing field addresses it), and fixable without retraining. Two of the six hypotheses
were **disproven** by existing fields — a useful, honest result that prevents wasted build
effort.

---

## 2. Results by Category

### 2.1 Negated skills (R301–R308) — ⭐ CONFIRMED (5/5)
The parser ignores negation and extracts denied skills, even **canonicalising** them:

| Test | Source wording | Extracted skill (verbatim) |
|---|---|---|
| **R302** | "No experience with Java." | `Java (Programming Language)` |
| **R303** | "Not proficient in C++." | `C++` |
| **R305** | "Expert in Python; **no experience with R**." | `R (Programming Language)` |
| **R306** | "Familiar with AWS, **but not Azure**." | `Microsoft Azure` |
| **R308** | skills line "Python, SQL **(not Tableau)**." | `Tableau (Business Intelligence Software)` |

R301 (positive control) extracted the real skills correctly; R304 ("limited exposure") and
R307 ("previously used… no longer") are genuinely partial and scored **ambiguous** (not
failures). **In every clear negation case, the denied skill was added to the candidate's
skills** — a false positive, not a missing representation.

### 2.2 Work authorisation (R309–R316) — DISPROVEN (field exists)
`data.workAuthorization` exists and is populated, e.g.
`R311 → "…Requires visa sponsorship to work in the U.S."`,
`R312 → "…Authorised to work in the U.S.; no sponsorship required"`. Hypothesis that work
authorisation is uncaptured is **false**. Caveat: it is a **free-text string** (no
citizen/PR/sponsorship enum, no expiry date), and in `R314` the field came back as the bare
label `"Work authorisation"`, **dropping the "expired in 2023" status** — a minor edge, not
a product gap.

### 2.3 Experience duration (R325–R332) — DISPROVEN (metrics exist)
`data.employmentMetrics` exists with `totalExperienceMonths`, `averageTenureMonths`,
`longestTenureMonths`, `currentRoleTenureMonths`, and `gaps`. Critically, for the
overlapping-roles probe **R327** (two concurrent 2020–present roles) it returned
`totalExperienceMonths: 83` — the single real span, **not** a doubled 166 — i.e. it did
**not** double-count the overlap. Duration handling is robust.

### 2.4 Employment type (R341–R348) — PARTIAL (enum incomplete)
`workExperience[].employmentType` exists and distinguishes several types, but the enum is
incomplete, so some arrangements are coerced to the nearest value:

| Test | Label in resume | `employmentType` returned | Verdict |
|---|---|---|---|
| R341 | Full-time, permanent | `full_time` | ✅ |
| R343 | Summer Internship | `internship` | ✅ |
| R345 | Freelance | `self_employed` | ✅ (reasonable) |
| **R342** | 6-month **contract** | `part_time` | ❌ no "contract" value |
| **R344** | **Volunteer** (unpaid) | `internship` | ❌ no "volunteer" value |

Contract and volunteer are **not representable** and get mis-mapped. Moderate, real, but an
extension of an existing field rather than a new capability.

### 2.5 Certification status (R333–R340) — REAL, but overlaps CareerGuard
`data.certifications` captures `{name, date}` only — **no status**:

| Test | Source | Returned |
|---|---|---|
| R333 (active) | valid through 2026 | `{name: "AWS Certified Solutions Architect", date: 2026}` ✅ |
| R334 (expired) | "expired 2022" | `{name: "PMP", date: 2022}` — reads like a valid date, **not "expired"** |
| R337 (revoked) | "revoked 2023" | `{name: "State license"}` — **status lost** |
| R339 (not awarded) | "coursework completed; exam not taken" | `{name: "Security+ coursework completed"}` — reads as held |

This is the *same shape* of problem as the education-status gap already captured by
**CareerGuard** — status (expired/pending/failed/revoked/not-awarded) is not preserved in a
structured field. Best treated as **extending CareerGuard to certifications**, not a
separate product.

### 2.6 Skill ownership (R317–R324) — REAL but ambiguous
Skills belonging to *people the candidate manages* are attributed to the candidate:
`R318 "Managed a team of 5 Python engineers" → skills include Python`;
`R320 "Oversaw a Kubernetes migration performed by the platform team" → Kubernetes`;
`R322 "My team wrote the service in Go" → Go`. Personal controls (R317, R321) are correct.
`skills[].sources` exists but models the *section*, not *ownership*. This is a genuine
semantic limitation, but over-attribution is defensible (a manager of Python engineers has
Python context) and cannot be scored a hard failure without an ownership model — recorded as
**ambiguous**, lower priority.

---

## 3. Confirmed Failures (exact JSON evidence)

All five are negated-skill false positives (§2.1). Example (`R306`), verbatim
`data.skills`: `[AWS → "Amazon Web Services", Computer Science, Azure → "Microsoft Azure",
backend services, data pipelines]` — the résumé states **"familiar with AWS, but not
Azure,"** yet **Azure is extracted and canonicalised to "Microsoft Azure."** Reproduced
identically for Java (R302), C++ (R303), R (R305) and Tableau (R308).

## 4. Where Affinda Performed Correctly

- Positive skills control (R301); negated **ambiguous** cases handled defensibly (R304, R307).
- Work authorisation captured (R311, R312) via a real field.
- Overlap **not** double-counted (R327); gaps/tenure metrics populated.
- Employment type correct for permanent, internship, freelance (R341, R343, R345).
- Active certification captured with date (R333).
- Personal-skill attribution correct (R317, R321).

## 5. Reproducibility

- **Negated skills:** fully reproducible — 5/5 clear negations failed identically.
- **Employment-type enum gaps:** reproducible for contract and volunteer specifically.
- **Certification status:** reproducible (0/8 carry a status field).
- **Skill ownership:** reproducible over-attribution, but inherently ambiguous.
- **Work auth / duration:** reproducibly **handled** (not gaps).

## 6. Existing Affinda Feature Overlap

Confirmed present in the responses (so **excluded** or **reframed** as opportunities):
`workAuthorization` (free-text), `employmentMetrics` (totals/gaps/tenure), `certifications`
(name+date), `workExperience[].employmentType` (enum), `skills[].sources`. The negated-skill
gap is **not** addressed by any of these; certification-status overlaps CareerGuard;
employment-type is an enum extension.

## 7. Customer Impact

- **Negated skills (high):** a candidate who writes "No experience with Java" is tagged with
  Java — they surface in Java searches and keyword-match scores they explicitly disclaimed.
  Directly corrupts shortlisting and ranking; silent (looks like a normal skill).
- **Employment type (moderate):** contract/volunteer mislabelled affects filters that
  distinguish employees from contractors/volunteers.
- **Certification status (moderate):** expired/revoked certs look valid — compliance risk
  (same class as CareerGuard's education issue).
- **Skill ownership (low–moderate, ambiguous):** inflated skill sets for managers.

## 8. Top Three Product Opportunities

1. **Negated-Skill / "Disclaimed Skills" detection** — flag or suppress skills the résumé
   explicitly denies ("no experience with X", "not proficient in X", "but not X", "(not X)").
   Post-extraction, no retraining: detect negation scope around each extracted skill in
   `rawText`, and emit `skills[].negated: true` or a separate `disclaimedSkills` list.
2. **Employment-type enum completion** — add `contract`, `volunteer`, `temporary` and map
   labels to them (extends an existing field).
3. **Certification-status enrichment** — add `certifications[].status`
   (active/expired/pending/revoked/not-awarded) — best shipped as a **CareerGuard extension**,
   since it is the same status-preservation pattern.

## 9. Ranking

Scores 1–5 (customer value · technical feasibility (4-day) · differentiation · evidence/repro
· before-after demo).

| # | Opportunity | Value | Feas | Diff | Evid | Demo | **Total** |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | **Negated-skill detection** | 5 | 5 | 5 | 5 | 5 | **25** |
| 2 | Certification-status (CareerGuard extension) | 4 | 4 | 2 | 4 | 4 | **18** |
| 3 | Employment-type enum completion | 3 | 4 | 2 | 3 | 3 | **15** |

## 10. Recommendation

**Build opportunity #1 — negated-skill detection.** It is the only genuinely *new* gap that
is strong-evidence (5/5), reproducible, customer-critical, uncovered by existing fields, and
feasible in four days as a post-extraction pass. #2 should be folded into CareerGuard rather
than built standalone; #3 is a minor enum extension.

**Required validation (held-out):** develop the negation rules on R301–R308, then generate a
**fresh, unseen** negation set — other verbs and structures ("without any X background", "X:
none", "no hands-on X", "do not list X as a skill", negation across a line break,
non-English negators) plus distractors where a skill legitimately appears near a negation of
*something else* — and report precision/recall so the fix is shown to generalise and not
over-suppress. Only then is a build justified.

---

## 11. Limitations

- 48 **synthetic** probes, **single run** — exploratory, not production rates; consistency
  not measured.
- "Disproven" means the hypothesised gap did not appear here (work auth, duration); it does
  not prove flawless behaviour at scale (e.g. `workAuthorization` is free-text and dropped an
  expiry once).
- Sandbox schema v1.0 exposes no per-field confidence; "status absent" is relative to this
  response shape.
- Skill-ownership over-attribution is recorded as an observation, not a scored failure; no
  claim is made about Affinda's internal model or root cause.

*Generated from `affinda-responses/round-3/round3-responses-48.json` via
`affinda-round3-tests/analyse_round3_results.py` (→ `affinda-round3-tests/findings/`).
Inputs unmodified; earlier rounds and reports untouched.*
