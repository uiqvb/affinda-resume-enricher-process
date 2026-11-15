# Affinda Resume Parser — Targeted Failure Investigation (Results)

*Evidence base: 45 controlled probe resumes (`T01–T45`) uploaded to the Affinda Sandbox;
actual responses in `affinda-resumes (1).json` (75 docs total — the 45 probes plus the
earlier 30). Scored by `affinda-targeted-tests/analyse_targeted_results.py` against
`ground_truth_targeted.json`. All values quoted here are from the real responses. No
live API calls; no fabricated data.*

---

## 1. Executive Summary

The three weaknesses flagged in the 30-resume study were stress-tested one variable at a
time. The result is decisive and, in two of three cases, **exonerating**:

| Area (origin) | Probes | Verdict |
|---|---|---|
| **Employer attribution** (D03) | T16–T30 | **Not a weakness.** 15/15 correct — the original error did **not** reproduce. |
| **Ongoing-employment dates** (D04) | T01–T15 | **Narrow, reproducible.** 13/15 correct; fails **only** with no current-keyword (bare dash / lone date). |
| **Education completion status** (F05) | T31–T45 | **Real, systematic, reproducible.** Status is never in a structured field (0/15); **6/15** emit a conferral date that misrepresents a non-completed qualification; 1 education entry dropped. |

**Tally across 45 probes: 30 pass · 7 inconclusive · 8 confirmed failures.**
Failure patterns: `misleading_completion` ×6, `invented_end_date` ×2, `education_dropped` ×1,
`status_absent` ×6 (inconclusive).

**Is it a good parser?** Yes — broadly very good. Of the three suspected cracks, one was a
non-issue (employer attribution is robust), one is a genuine but **narrow** edge case
(keyword-less current dates), and **one is a clean, customer-impacting, reproducible
weakness: education completion status.** That single finding is the justified basis for a
four-day prototype; the other two are not.

---

## 2. Dataset & Methodology

45 resumes, 15 per phase, each holding everything fixed except one controlled variable
(`ground_truth_targeted.json` / `test_manifest_targeted.csv`). Paired layout controls
isolate layout from content (T13/T14 two-column & table dates; T29/T30 two-col vs single;
T44/T45 flow vs table education). Responses read against the observed schema
(`data.person.name`, `data.contact`, `data.workExperience[].dateRange`, `data.education`,
`data.rawText`, `meta.document`). Only unambiguous expectations are scored pass/fail;
ambiguous outcomes are preserved as **inconclusive**. Per the brief, an open-ended date
left *unknown* is acceptable — only a **fabricated** value is a failure.

---

## 3. Phase 1 — Ongoing-employment dates (T01–T15)

**13/15 pass. The parser handles every current-employment keyword correctly and only
fails when no keyword is present.**

| Trigger | Tests | Result |
|---|---|---|
| Explicit keyword — "Present", "Current", "to date", "Since", "Ongoing", "onwards", "Now", "currently employed", year-only+Present | T01, T02, T04–T10 | ✅ `end.current = true`, no fabricated date |
| Keyword inside two-column / table / with overlapping role | T13, T14, T15 | ✅ current recognised; layout no effect |
| Completed control "Oct 2021 – Oct 2024" | T11 | ✅ end 2024, not current |
| **Bare trailing dash "October 2021 –"** | **T03** | ❌ `start=2021-10, end=2021-10, durationMonths=1, current=false` |
| **Single date "October 2021"** | **T12** | ❌ `start=2021-10, end=2021-10, durationMonths=1, current=false` |

**Finding.** This exactly reproduces and **bounds** the original D04 bug: with no
recognised current-keyword, Affinda **fabricates an end date equal to the start**, turning
an open-ended role into a 1-month stint. Adding *any* of the ten keyword forms fixes it.
Per the brief's nuance, the failure is not "didn't set current" (leaving end unknown would
be acceptable) — it is **inventing a concrete, wrong end date**.

**Reproducibility:** high, but only under the keyless condition. **Real-world exposure:**
bounded — most resumes write "Present"/"Current"; the exposed population is résumés using a
dangling dash or a lone start date.

---

## 4. Phase 2 — Employer attribution (T16–T30)

**15/15 correct. The original D03 "employer bleed" did NOT reproduce.** Evidence
(organization per role, from the raw responses):

| Test | Scenario | Parsed employer(s) | OK |
|---|---|---|---|
| T16 | "Self-Employed" | `Self-Employed` | ✅ |
| T17–T19 | Independent / Independent Contractor / Sole Trader | label preserved | ✅ |
| T20 | **No employer line** | `organization: null` (not borrowed) | ✅ |
| T21 | freelance alongside permanent (perm first) | `Meadowlark Software` + `Self-Employed` | ✅ **no bleed** |
| T22 | freelance above permanent | `Self-Employed` + `Meadowlark Software` | ✅ **no bleed** |
| T25 | consulting w/ multiple clients | `Self-Employed` (clients **not** promoted to employer) | ✅ |
| T26 | business-name self-employment | `Chen Creative Studio` | ✅ |
| T27 | via staffing agency | `TechStaff Inc.` | ✅ |
| T28 | three concurrent roles | all three distinct | ✅ |
| T29 / T30 | two-column vs single (paired) | identical, correct | ✅ |

**Finding.** Employer attribution is **robust**, including the direct D03 analog
(freelance alongside permanent) and the hard cases (no employer, clients, agency). The
single D03 observation in the earlier run appears **idiosyncratic / non-reproducible** — a
weak basis for any product work. (Caveat §8: D03's exact token layout — "Freelance
Illustrator (Self-Employed)" as the *title* with employer "Independent", inside a 3-role
overlap — was approximated, not byte-identical.)

---

## 5. Phase 3 — Education completion status (T31–T45) — the real finding

**Status is represented in a structured field in 0 / 15 tests.** The behaviour splits
cleanly on whether the entry carries a terminal year:

### 5.1 Misleading conferral dates — 6 confirmed failures
When the entry contains an end year, Affinda emits it as a conferral-style
`dateRange.end.date` with **no status field**, even against explicit non-completion wording:

| Test | Source wording | `education.end` returned | Why it misleads |
|---|---|---|---|
| **T33** | "Expected graduation 2027" | **`2027-01-01`** | future date shown as a conferral |
| **T37** | J.D. "Expected completion 2027" | **`2027-01-01`** | future date shown as a conferral |
| T35 | M.Eng "Not completed" | `2023-01-01` | reads as an earned master's |
| T36 | J.D. "Incomplete" | `2023-01-01` | reads as an earned J.D. |
| T40 | B.Com "Withdrawn" | `2020-01-01` | reads as an earned degree |
| T42 | Diploma "coursework completed, **qualification not awarded**" | `2020-01-01` | reads as an awarded diploma |

A recruiter (or downstream filter) reading structured output alone would count all six as
**completed, conferred qualifications**. T33/T37 are the sharpest: a **future** "conferral"
in 2027 for a degree that is not yet earned.

### 5.2 Status-absent (no false date, but still no status) — 5 inconclusive
When the entry says "present / in progress / candidate / enrolled / deferred", Affinda sets
`end.current = true` (no false conferral date) — better — but still carries **no status
field**: T32 (currently studying), T34 (in progress), T38 (PhD candidate), T41 (deferred),
and T44's in-progress M.Eng. Status is recoverable **only from `rawText`** (verified: the
words "Incomplete", "Withdrawn", "not awarded", "Expected", etc. are present in `rawText`
for every case).

### 5.3 Dropped — 1
**T43** ("Certificate IV in Cybersecurity, TAFE NSW — Currently enrolled") →
`education: []`. The qualification was **dropped entirely** from structured output.

### 5.4 Completed controls — correct
T31 (BSc, 2023), T39 (PhD, 2024), T44-BSc (2020) all returned the right conferral year —
confirming the issue is *status representation*, not date extraction.

**Finding.** Across 15 status variants, **not one** produced a structured status signal, and
**6** actively misrepresented a non-completed qualification as conferred (two with future
dates). This is **systematic, reproducible, and directly harmful to recruitment data
quality.**

---

## 6. Which failures are reproducible vs ambiguous-only

- **Fully reproducible, systematic:** education status (Phase 3) — 6/6 year-bearing
  non-completed degrees misrepresented; 0/15 status fields.
- **Reproducible under a narrow, identifiable condition:** keyless current dates
  (T03/T12) — fails iff no current-keyword.
- **Ambiguous-only / did not reproduce:** employer attribution (Phase 2) — 0 failures.

## 7. Recruitment data-quality impact

- **Education status (high):** candidates with in-progress, withdrawn, or not-awarded
  qualifications can be surfaced as fully qualified — a direct screening/compliance risk
  (e.g. "has J.D." filters, regulated roles). Future-dated conferrals (2027) could also
  break date logic.
- **Keyless current dates (low–moderate):** a current employee can appear to have a
  1-month-old ended role; bounded to résumés without a "Present"-type keyword.
- **Employer attribution (none observed):** robust.

## 8. Existing Affinda capabilities (already accounted for)

From the bundled Affinda reference: per-field **confidence**, LLM **validation rules**,
**human-review** queue, **model memory**, **data sources** (value normalisation),
**transformation prompts**. So a fix must **not** be generic confidence/validation/review.
The gap here is specific and uncovered: **no education `status` concept** in the resume
schema, and **no structured distinction between a conferred date and an expected/terminal
date**. Neither is addressed by the features above.

## 9. What can be fixed without retraining

The strongest opportunity is **post-extraction, no model retraining required**: the status
evidence already reaches `rawText` and the suggestive signals (future end date, explicit
"incomplete/withdrawn/expected/not awarded" tokens) are present. A derived
`education[].completionStatus` field + a "date is expected, not conferred" flag can be
computed from existing output.

## 10. Ranked opportunities

Scores 1–5 (evidence · reproducibility · customer impact · differentiation vs §8 ·
4-day feasibility · before/after demo).

| # | Opportunity | Ev | Repro | Impact | Diff | Feas | Demo | **Total** |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | **Education completion-status enrichment** (derived `completionStatus` + expected-vs-conferred date flag) | 5 | 5 | 5 | 4 | 5 | 5 | **29** |
| 2 | Keyless current-date normalisation (open-ended → ongoing, not 1-month) | 4 | 4 | 3 | 3 | 4 | 3 | **21** |
| 3 | Employer attribution hardening | 1 | 1 | 2 | 2 | 2 | 1 | **9** |

## 11. Recommended Four-Day MVP

**#1 — Education Completion-Status enrichment.** A post-extraction enricher that adds, per
education entry, `completionStatus ∈ {completed, in_progress, expected, discontinued,
not_awarded, unknown}` and `dateIsExpected: bool`, derived from (a) `end.current`, (b) a
future end date relative to processing, and (c) status tokens in `rawText`/description.

- **Why it wins:** only finding that is strong-evidence **and** systematic **and**
  customer-critical **and** feasible without retraining **and** demos vividly (6 résumés
  flip from "looks conferred" to correctly flagged).
- **Deliverables:** `enrich_education(response) -> response+status`, a JSON field spec, and
  a before/after table over T31–T45.
- **Held-out validation (required):** build the rules on T31–T45, then generate a **fresh,
  unseen** status set (new phrasings: "sabbatical", "ABD", "thesis pending", "credits
  short", non-English month formats, transcripts-style entries) and report generalisation —
  so the fix is shown to work beyond the development cases.
- **Milestones:** D1 status-token + future-date detectors; D2 `completionStatus` derivation
  + field spec; D3 held-out generalisation set + tuning; D4 before/after demo + write-up.

> Recommended **because** the evidence supports it (6/6 reproducible, 0/15 status fields).
> Opportunity #2 is a worthwhile smaller fix; #3 is not pursued (no observed failure).

## 12. Limitations

- 45 **synthetic** probes, **single run** — exploratory, not production rates; consistency
  not measured.
- Sandbox schema (v1.0) exposes **no per-field confidence or document warnings**; "status
  absent" is relative to this response shape (the platform API may expose more).
- Phase 2 did not byte-replicate D03's exact token arrangement; "not reproduced" means the
  effect is at most rare/fragile, not provably impossible.
- Status tokens confirmed present in `rawText`; no claim is made about Affinda's internal
  model or root cause.

---

*Generated from `affinda-resumes (1).json` via `affinda-targeted-tests/analyse_targeted_results.py`
(→ `affinda-targeted-tests/findings/`). Inputs unmodified; the original 30-resume study and
`AFFINDA_ANALYSIS.md` are untouched.*
