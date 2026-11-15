# Day 1 & 2 Recap — ResumeGuard

> **What this is.** A plain-English recap of the first two days of ResumeGuard, plus a
> section that **defends the enrichment choices** with the actual tests and numbers behind
> them. Everything here is traceable to the Day-1 analysis files
> (`DAY-1 - Ideation/AFFINDA_ANALYSIS.md`, `DEFECT_REPORT.md`, round analyses) and the Day-2
> experiment (`DAY-2 - Planning/`). No number is hand-counted — all verdicts come from scoring
> real Affinda Sandbox responses against local ground truth with committed Python.

---

## 0. The one-paragraph story

**Day 1 (Ideation)** probed Affinda with **183 synthetic resumes across 4 falsification
rounds**, discovered that its *extraction* is nearly flawless but its *status/temporal
reasoning* drops meaning, eliminated the weak ideas, and landed on **three evidence-backed
enrichment gaps** → deliverable `ROUGH_SCOPE.md`. **Day 2 (Planning)** reproduced all three
gaps at scale on **300 freshly scored resumes**, confirmed against Affinda's own docs that the
missing fields genuinely aren't in the schema (so we *add* value, never duplicate it), and
locked a complete build-ready design → deliverables `DESIGN.md` + `BUILD_PLAN.md`.

| Day | Phase | Deliverable | Headline |
|---|---|---|---|
| **1** | Ideation | `ROUGH_SCOPE.md` | 183 resumes, 4 rounds → 3 proven gaps, weak ideas killed |
| **2** | Planning | `DESIGN.md` + `BUILD_PLAN.md` | 300 scored resumes → gaps confirmed at scale, D1–D9 locked |

---

## 1. Day 1 — what was run, seen, and noticed

### 1.1 The experiments (probe → falsify → hunt → falsify)

| Round | Resumes | Purpose |
|---|---|---|
| **R1** | 30 | "What breaks the parser?" — broad net, 6 categories (A–F) |
| **R2** | 45 | Falsify the 3 R1 anomalies (D03, D04, F05) |
| **R3** | 48 | Hunt wider — 6 new weakness categories |
| **R4** | 60 | Falsify the R3 survivors with matched controls |

Round 1's six categories: **A** baseline · **D** complex employment · **E** layout complexity
· **F** ambiguity/contradictions · **B** hidden text · **C** AI-instruction/prompt-injection.

### 1.2 The big surprise: core extraction is nearly flawless

On the 20 main resumes: **name 20/20, email 20/20, phone 20/20, roles 45/46, titles 45/45,
start dates 45/45, end/current 44/45, education present 20/20, skills recall 0.96.** Layout
did not break it — two-column, tables, even a **scanned OCR-only** PDF returned every field
correctly (just slower: 5.2 s vs ~0.1–0.9 s). **Conclusion: layout is not a failure mode.**

The weaknesses were all in one place — **temporal and status reasoning**: whether something is
*finished, valid, current, or actually possessed*. That single thread became the product.

### 1.3 The 11 shortcomings, ranked by what survived falsification

| # | Area | Evidence | Verdict |
|---|---|---|---|
| 1 | **Negated skills** | **12/12** clean negations failed (reproduced R3 *and* R4) | **Build V1** |
| 2 | **Education completion status** | **0/16** had a status; 7 misleading conferrals, 6 absent, 1 dropped | **Build V1** |
| 3 | **Certification validity** | **0/18** had a status; expired/revoked read as valid | **Build V1 (w/ edu)** |
| 4 | **Open-ended employment dates** | 5/5 *keyless* roles → fake 1-month job; 14/14 keyed = fine | **Build V1 (cheap)** |
| 5 | Employment type/classification | 9/18 lossy (part-time→full-time) | V2 |
| 6 | Work authorisation | 7/18 partial — field already exists | V2 |
| 7 | **Hidden/invisible PDF text** | 5/5 reach rawText, 0/5 corrupt, no warning | V2 (VisibleProof) |
| 8 | Skill ownership | 12 ambiguous, **0 confirmable** | Defer |
| 9 | Employer attribution | **Did not reproduce — 15/15 clean** | Drop |
| 10 | Experience-duration totals | 16/16 correct, overlap not doubled | Drop |
| 11 | AI instruction-following | **0/5** — never obeyed | Drop (reassuring) |

### 1.4 How the keep/drop decisions were made

1. **Falsification, not confirmation.** Every R1 anomaly had to survive a targeted retest.
   This is what killed **employer attribution** (looked real in R1's D03, then **15/15 clean**
   across R4's variations — a fluke).
2. **Three honest buckets.** *Confirmed mistake* (wrong value) vs *missing information*
   (meaning in text but not structured) vs *ambiguous* (unscorable). Only *missing
   information* makes a clean enrichment product.
3. **"Does Affinda already ship it?"** Hard filter — excluded per-field confidence, validation
   rules, human review, skill normalisation. This demoted **work auth** (field exists) and
   dropped **duration totals** (already robust).
4. **"Does a human catch it anyway?"** Weighted *automated downstream screening* — an ATS
   filtering on "has J.D." or "knows Java" acts on the structured field, no human in the loop.

### 1.5 Invisible text — the correct version, and why it was parked

- **Invisible text DOES enter the parse.** All 5 hiding techniques landed in `rawText`
  (**5/5**) — Affinda reads the text layer regardless of visibility, even ignoring the CropBox
  and reading text *under* an opaque fill. It just never **corrupted** a structured field
  (**0/5**), and gave **no warning**.
- The one thing never extracted was **PDF annotation text** (C04) — a different PDF object,
  not invisible body text.
- **Parked (→ V2 "VisibleProof") because:** it's a *trust/integrity* observation, not an
  accuracy defect; the paired injection tests were **0/5** (no proven harm); and it's a
  *different discipline* — PDF forensics on the original file (render mode, font size, colour,
  CropBox via PyMuPDF), not JSON enrichment. Affinda's JSON can't tell you *which* rawText was
  invisible, so it doesn't fit our JSON-in contract without also passing the PDF.

---

## 2. Day 2 — proving it at scale, then locking the design

### 2.1 Sprint 1 — the 300-resume experiment

Generated **300 synthetic resume PDFs** (100 education, 100 certification, 100 skill) from the
taxonomy CSVs, parsed all through the Affinda Sandbox, and scored against ground truth with
`score_experiments.py`. Findings split into **two separate lists**: 📘 **List A** = the three
enrichment opportunities (the product); 🐞 **List B** = genuine parser bugs (a courtesy list
for Affinda, *not* something we build on).

**Headline at scale — the cause is structural (`0/100` carry a status field in any case):**

| Gap | Result at scale | Control (proves signal ≠ noise) |
|---|---|---|
| Certification validity | **33/36** expired/revoked/suspended read as **valid** | 22/24 valid certs correct |
| Education status | **20/22** "expected"/"withdrawn" degrees → year as a conferral end-date | 9/10 completed degrees correct |
| Skill claims | **9/10** denied skills surfaced as possessed | 14/16 expert skills correct |

**Confirmed non-duplicative:** Affinda's own docs show `completionStatus` / `validityStatus` /
`claimStrength` are **absent from the fixed v1 schema**. **Correction logged:** old "Defect 5"
(Certificate-IV routing to `certifications`) is *documented behaviour*, not a bug — so our
education module must also read the `certifications` array.

### 2.2 Sprint 2 — nine decisions locked (D1–D9)

D1 four feature modules (v1 = Skill, Education, Certification; Employment-Date = V2
fast-follow; edu+cert share one status engine) · D2 separate parallel enrichment block,
original returned byte-for-byte untouched · D3 evidence = quote + rawText char offsets · D4
status vocabularies per module · D5 entity-anchored 3-step detection + adjacency precision
rule · D6 grade on a **new blind batch**, measure first then set the bar · D7 ship 4 interfaces
in 3 iterations · D8 Python 3.11 + `regex` + typer + FastAPI + Docker · D9 v1 includes both
List-B helpers (date caveat + missing-entity flag). Architecture = **feature-sliced modular
monolith**, confirmed by an independent zero-context agent review.

---

## 3. Defending the enrichment choices (the part that matters)

For each chosen enrichment: **the gap → the evidence → the control that proves it's real → the
real-world harm → why it's worth building.** The pattern across all three is identical and
that's the point — Affinda **extracts the entity correctly but discards the qualifier**, and
the qualifier is exactly what an automated hiring pipeline acts on.

### 3.1 Why this evidence is trustworthy (before the specifics)

- **Synthetic + ground truth + committed Python scoring** — zero hand-counting, reproducible.
- **Falsification rounds** — findings had to survive a deliberate attempt to disprove them
  (and one, employer attribution, didn't — so it was dropped, which proves the method bites).
- **Matched controls every round** — positive cases must pass while negatives fail; if the
  control failed too, the finding would be noise. The controls held.
- **Confirmed against Affinda's docs** — the missing fields are genuinely not in the schema,
  so this is *additive*, never a reimplementation of something shipped.

### 3.2 Enrichment 1 — Skill claim strength / negation  *(Problem A)*

**The gap.** A denied, weak, or aspirational skill is extracted as a *possessed* skill, with
the qualifier flattened away.

**The evidence.**
- Round 1→4: **12/12 clean negations failed** — e.g. `"No experience with Java"` → **Java
  extracted**; `"Familiar with AWS, but not Azure"` → **Azure extracted** (even canonicalised
  to "Microsoft Azure"); `"Python, SQL (not Tableau)"` → **Tableau extracted**.
- **Reproduced independently in two separate rounds (R3 and R4)** — not a one-off.
- At scale (Day 2): **9/10 denied skills surfaced as possessed**, and all weak/aspirational
  wording ("learning", "basic exposure") was flattened to a bare skill.

**The controls (why it's signal, not noise).**
- Positive controls passed: `"Skills: Python, SQL, Docker"` and `"Expertise in Python,
  Kubernetes, SQL and Azure"` → all extracted correctly.
- **14/16 expert skills** correctly captured at scale.
- A genuine distractor was handled correctly: `"Not certified in AWS, but use AWS daily"` →
  **AWS kept** (a *certification* denial, not a *skill* denial). The parser isn't blindly
  wrong; it's specifically blind to negation of possession.
- The honest boundary: soft wording (`"limited exposure"`, `"previously used… no longer"`) is
  genuinely ambiguous and we don't claim those as failures.

**The real-world harm.** An ATS that filters candidates on "has Java / has Azure / has
Tableau" will **surface the exact candidates who wrote that they can't do it.** This is a
false *positive* in hiring — the most expensive kind, because the candidate advances on a skill
they explicitly disclaimed.

**Why worth building.** `claimStrength` is absent from Affinda's schema (non-duplicative); the
fix is a small closed set of qualifier cues over entities Affinda already found (feasible);
and it's demoable live. Scope is the **whole strength range** (expert → intermediate → basic →
learning → no-experience), not just a yes/no — List A item 3.

### 3.3 Enrichment 2 — Education completion status  *(Problem B)*

**The gap.** In-progress, withdrawn, incomplete, deferred, and not-awarded degrees are recorded
as **completed**, often with the terminal year emitted as a conferral-style end date.

**The evidence.**
- **0/16 education entries carried any status field** — the loss is *systematic and
  structural*, not occasional.
- 7 outright misleading conferrals: `"Master NOT completed"` → `end 2023` (reads as earned);
  `"withdrawn"` → `end 2020`; `"coursework completed, qualification NOT awarded"` → `end 2020`.
- **Logically impossible cases slip through:** `"Expected graduation 2027"` → `end 2027` shown
  as a conferral — a *future* "completion date".
- At scale: **20/22 "expected"/"withdrawn" degrees returned the year as a conferral-looking
  end date.**

**The controls.** Completed-degree controls passed — `"completed"` → correct conferral year;
`"PhD awarded 2024"` → correct; **9/10 completed degrees** correct at scale. So the parser gets
genuine graduates right; it only loses the *non-completion*.

**The real-world harm.** A recruiter pipeline filtering on "has a J.D." or "holds a Master's"
will **count withdrawn and still-enrolled candidates as graduates.** The flagship case (F05): a
J.D. marked "INCOMPLETE, expected 2026" came back as a completed master's — a downstream
"qualified lawyer" filter would wrongly include them.

**Why worth building.** `completionStatus` is absent from the schema; the signal is the
strongest "missing information" defect in the whole study (0/16); and it shares its entire
engine with certification validity (below), so two enrichments cost barely more than one.

### 3.4 Enrichment 3 — Certification validity  *(Problem C)*

**The gap.** `certifications` stores `{name, date}` only — an **expired, revoked, or suspended**
credential keeps a date that *reads as valid*.

**The evidence.**
- **0/18 certifications carried a status.** Expired/revoked/suspended all extract with a plain
  date and no flag: `"PMP — expired 2022"`, `"Chartered Engineer licence — revoked 2024"`,
  `"Professional licence — temporarily suspended"` — status lost in every case.
- At scale: **33/36 expired/revoked/suspended certs read as valid** — the single strongest
  at-scale number in the project.

**The controls.** Active/renewed certs captured fine (5 pass: `"AWS SA — active, valid through
2027"`, `"PMP — renewed 2025"`, `"CISSP — active"`); **22/24 valid certs** correct at scale.
And the only *drops* are defensible — scheduled-but-not-taken and attempted-and-failed exams
(`"Security+ — scheduled, not yet attempted"`) aren't held credentials, so dropping them is
reasonable, not a defect we'd need to fix.

**The real-world harm.** This is the highest-stakes gap: a **revoked engineering licence** or an
**expired CISSP** reading as a current credential is a compliance and safety exposure, not just
a hiring inconvenience. Regulated roles (medical, legal, engineering, security clearance) screen
on exactly this field.

**Why worth building.** `validityStatus` is absent from the schema; it's the same *status-loss
shape* as education, so both run through **one shared status engine** (build once, serve two
enrichments) — the reason D1 pairs them.

### 3.5 Enrichment 4 (V2 fast-follow) — Open-ended employment dates  *(Problem D)*

**The gap.** A current role written **without a recognised keyword** gets a fabricated end date
equal to its start → a fake **1-month job**.

**The evidence.** **5/5 keyless variations failed** (`"October 2021 –"` dangling dash;
`"October 2021"` lone date) → end = start. But **14/14 variations with any keyword** (Present,
Current, Ongoing, "to date", "since 2021", even year-only "2021 – Present") were **correct**.

**The controls.** The 14 keyed passes *are* the control — the trigger is narrow (keyless only)
but **100% reproducible inside that trigger**, and it corrupts both role status *and* duration
metrics.

**Why V2, not V1.** The cheapest possible fix (flag "end == start with no supporting keyword;
don't assume ongoing"), but it needs its own taxonomy + 100-resume validation set before it
earns a module — so it's a deliberate fast-follow, not a cut.

### 3.6 The choices in one table

| Enrichment | Core number | At scale | Control held | Schema has it? | Real-world harm |
|---|---|---|---|---|---|
| **Skill claim** | 12/12 negations fail | 9/10 denied → possessed | 14/16 expert ✓ | ❌ no `claimStrength` | Surfaces candidates who disclaimed the skill |
| **Education status** | 0/16 status; 7 false conferrals | 20/22 withdrawn → grad date | 9/10 completed ✓ | ❌ no `completionStatus` | Counts non-graduates as graduates |
| **Cert validity** | 0/18 status | 33/36 invalid → valid | 22/24 valid ✓ | ❌ no `validityStatus` | Revoked/expired licence reads as current |
| **Open-ended dates (V2)** | 5/5 keyless fail | — | 14/14 keyed ✓ | partial | Fake 1-month job; corrupts duration |

**The unifying argument.** All three (four) are the *same defect class* — Affinda nails the
**entity**, discards the **qualifier** — and the qualifier is precisely what an automated
screen acts on. They're proven (reproduced + at scale), real (controls held), additive (absent
from the schema, so no duplication), feasible (closed cue-sets over already-extracted
entities), and high-stakes (false positives in hiring and compliance). That's why these were
taken and the rest were parked or dropped.

---

## 4. The parser defects we found (List B — the courtesy bug list)

These are **separate from the product.** List A (above) = *missing status fields* we add. List
B = *genuine Affinda extraction bugs* we found while testing and logged for Affinda. **We did
not — and cannot — "solve" these**; the parser is a closed black box we don't own. We can only
*find* them, and *flag* the few that are flaggable from the JSON. Every ID is reproducible from
the saved Sandbox responses.

| # | The bug | Evidence | Can our tool help? |
|---|---|---|---|
| **1** | **Mid-tier skills dropped inconsistently** — Azure/Tableau/Spark silently discarded depending on surrounding words; top skills always survive | Azure **3/8**, Tableau **4/8**, Spark **6/8** vs Python/Java/SQL/AWS **9/9**. "8+ years of Azure" → dropped, identical "8+ years of Java" → kept | **Flag only** (skill is gone before we run; scan rawText and warn) |
| **2** | **"Bar admission" never extracted** — a real legal credential dropped in every context | **7/7** (C010, C022, C034…) return no Bar entry; no other cert name ever dropped | **No** (nothing in output to annotate) |
| **3** | **"Withdrawn 2020" emitted as a graduation end-date** — unfinished degree becomes identical to a conferred one | **9/9** "withdrawn" + **11/11** "expected <future year>" put the year in `end` | **Partial** (we add `completionStatus`; the bad date stays) |
| **4** | **"Juris Doctor (JD)" truncated + tagged `master`** (should be doctoral) | E053 | **No** (truncation looks common — Affinda's own docs show "Bachelor of") |

**One honest retraction:** we logged a "Defect 5" (certificate-level quals landing in
`certifications` not `education`), then read Affinda's docs and found it's *documented, intended
behaviour* — so we deleted it. The testing was rigorous enough to catch our **own** mistake,
not just Affinda's. (Consequence: our education module must also read the `certifications`
array.)

---

## 5. What's PROVEN vs what's still UNMEASURED (read before claiming anything)

The single most important honesty line in this project: **we have rigorously measured the
*problem*. We have NOT yet measured the *solution*.** Keep these two apart.

| | Status | Backed by |
|---|---|---|
| **The gaps are real** (problem proven) | ✅ **Strong** | **~483 synthetic resumes** (183 Day 1 + 300 Day 2), each parsed live and scored by committed Python vs ground truth — no hand-counting |
| **The gaps aren't already in the schema** (non-duplicative) | ✅ Confirmed | Checked against Affinda's published v1 contract |
| **The tool runs & is internally correct** | ✅ Partial | Runs end-to-end (`python main.py`); **34 stdlib `unittest` tests pass**; two of our own bugs fixed during build |
| **How accurate the tool is on unseen resumes** | ❌ **Not measured yet** | The D6 eval (a fresh **blind** batch, measure-first-then-set-the-bar) is **deferred/not built**. The 300 are only a dev sanity-check |

**So if asked "how well does your enricher perform?" — the honest answer today is: we don't
have that number yet.** We proved the problem (483 resumes) and built a working, unit-tested
tool; we have not yet graded the tool on unseen data. That is the next milestone — deliberately
designed (blind batch), not skipped. Saying this out loud is a feature: it shows the difference
between *proving the problem* and *proving the fix* was understood, not blurred.

---

*Sources: `DAY-1 - Ideation/{AFFINDA_ANALYSIS.md, DEFECT_REPORT.md, TARGETED_ANALYSIS.md,
ROUND3_ANALYSIS.md, ROUND4_ANALYSIS.md}`, `DAY-2 - Planning/{DAY2_LOG.md, experiments/findings/}`,
`DESIGN.md`, `BUILD_PLAN.md`. All verdicts scored from real Sandbox responses; 183 resumes Day 1,
300 Day 2; synthetic, single-run, Sandbox schema v1.0 (no per-field confidence).*
