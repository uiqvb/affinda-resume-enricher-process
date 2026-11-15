# Day 2 — Planning — Sprint 1 & Sprint 2 Log

> **Phase:** Planning.  **Main achievement / deliverable:** `DESIGN.md` (+ `BUILD_PLAN.md`) —
> the build-ready design. Proved all 3 enrichment gaps with 300 scored resumes, locked every
> Sprint-2 decision (D1–D9) and the architecture. Output = **the Design Doc.**

*End-of-day retrospective for Day 2 (2026-11-13). Day 1 ended with three evidence-backed
product directions and a modular plan; Day 2 turned one of them — the enrichment layer — into
a proven opportunity and a fully-scoped, build-ready design. Two sprints, ~2 hours each.*

---

## Sprint 1 · The 300-résumé experiment (reproduce the gaps at scale)

**Question:** Do the Day-1 anomalies hold up across 100 controlled résumés per problem, and
are they *missing fields* we can add — or just the parser getting values wrong?

### What was done
- **Generated 300 synthetic résumé PDFs** — 100 education, 100 certification, 100 skill —
  from the three taxonomy CSVs via `experiments/build_experiments.py` (fixed a missing
  `layout` column for the skill set).
- **Parsed all 300 through the Affinda Sandbox**, then scored every response against local
  ground truth with `experiments/score_experiments.py` (no hand-counted numbers).
- **Split the findings into two separate lists** (see `experiments/findings/README.md`):
  - **📘 List A — enrichment opportunities** (`LIST-A_RESULTS.md`): the three missing
    qualifier fields = **the product**.
  - **🐞 List B — parser defects** (`LIST-B_PARSER_DEFECTS.md`): genuine extraction bugs,
    kept separate as a courtesy list to show Affinda — *not* what we build on.

### Results (headline)
- All three gaps reproduced; the cause is **structural** — `0/100` entries carry a
  completion-status / validity / claim-strength field in any case.
- **33/36** expired/revoked/suspended certs read as valid.
- **20/22** "expected"/"withdrawn" degrees return the year as a conferral-looking end date.
- **9/10** denied skills ("no experience with…") surface as possessed; all weak/aspirational
  claims flattened.
- **Controls held** (9/10 completed degrees, 22/24 valid certs, 14/16 expert skills) — so the
  signal is real, not noise.

### Confirmations & corrections
- Read Affinda's official parse-response docs → confirmed `completionStatus` /
  `validityStatus` / `claimStrength` are **absent from the fixed v1 schema**. We add value,
  we don't duplicate the parser.
- **Retracted old "Defect 5"** (Certificate-IV routing to `certifications`) — it's
  *documented behaviour*, not a bug. (Consequence: our education module must also read the
  `certifications` array.)
- Logged a real skill-salience defect in List B: Azure/Tableau/Spark dropped in
  parenthetical/prose placement while Python survived.

### Produced
- Two saved artifacts: the **interactive taxonomy viewer** and the **parser-vs-enrichment
  divergences visual** (only the important/divergent cases).

**Outcome:** the enrichment layer went from "promising Day-1 finding" to a measured,
reproducible, non-duplicative opportunity with ground-truth numbers behind it.

---

## Sprint 2 · Scope & design (plan everything so tomorrow is pure build)

**Question:** Can we lock every technical decision — stack, data flows, logic, regex, file
structure — with the human making each call, so Day 3 is execution only?

### Decisions locked (D1–D9, in `BUILD_PLAN.md §0`)
- **D1** 4 feature modules, each its own self-contained blob (v1 = Skill, Education,
  Certification; Employment-Date is a V2 fast-follow). Education + certification share an
  invisible internal status engine.
- **D2** Separate parallel `resumeGuard` block; Affinda's `data` returned byte-for-byte
  untouched; referenced by array index.
- **D3** Evidence = quoted snippet **+** `rawText` character offsets.
- **D4** Status vocabularies per module (the annotation field is `status`).
- **D5** Entity-anchored 3-step detection + adjacency precision rule; when unsure → stay safe.
- **D6** Grading on a **new blind held-out batch** (fresh agent told *what*, not *how*);
  **measure first, set the bar after**.
- **D7** Ship **all four interfaces in 3 iterations** (library+CLI → +API → +dockerized API).
- **D8** Tech: Python 3.11+, `regex` (fuzzy) brain, typer CLI, FastAPI+uvicorn API,
  Docker+compose, pytest.
- **D9** v1 includes **both** List-B helpers: date caveat + missing-entity flag.

### Design work
- Wrote **`DESIGN.md`** — the full build-ready blueprint (tech stack, file tree, data shapes,
  every flow with pseudocode, the actual regex tables, validators, build sequence).
- Began the **plain-English walkthrough** of DESIGN.md, one piece at a time, human-driven:
  - **Piece 1 — the shape:** one `enrich()` function; original deep-copied and proven
    untouched by a final `assert`; our labels in a separate `resumeGuard` block; every
    annotation carries its evidence (quote + char span).
  - **Piece 2 — the file tree:** restructured into a **feature-sliced modular monolith**
    (`shared/` → `modules/<feature>/` → `app/` → `delivery/`, one-way dependencies, one
    boundary test). Chosen over two alternatives and **confirmed by an independent
    zero-context agent review** — not just agreement.
  - **Piece 3 — Flow A (`app/enrich.py`):** the manager pattern — validate → deepcopy → loop
    the registry calling each feature's `run()` → roll up findings → assert untouched →
    return. Adding a V2 feature = one folder + one registry line.
- **Renamed the annotation fields** everywhere for readability: `entryIndex` (was index),
  `entity` (was name), `status` (was label); skill value `no_experience` (was none).

**Outcome:** all nine decisions locked, the architecture settled and externally sanity-checked,
and three of the design pieces walked through with the human fully in the loop.

---

## What's done vs. what's left

| | Status |
|---|---|
| 300 résumés generated, parsed, scored | ✅ done |
| Two findings lists (A opportunities / B defects) | ✅ done |
| Enrichment confirmed non-duplicative (vs docs) | ✅ done |
| All 9 build decisions (D1–D9) | ✅ locked |
| `DESIGN.md` blueprint | ✅ written |
| DESIGN.md walkthrough | 🔵 pieces 1–3 of ~8 done |
| Remaining walkthrough (tomorrow) | ⏭ Piece 4 locator · 5 regex rules · 6 skill checker + precision guard · 7 status engine · 8 validators + grader |
| Implementation | ⏭ Day 3, per `DESIGN.md §11` build order |
| Blind test batch (D6) | ⏭ generate via a fresh, context-free agent |

> **Note:** `DESIGN.md §8` (eval harness pseudocode) still reads "reuses the 300" — stale
> against the locked D6 blind-batch decision; to be corrected when Piece 8 is walked.

**In one sentence:** Day 2 took the enrichment idea from a Day-1 hunch to a measured,
documented opportunity (300 résumés, two clean lists) and a fully-scoped, externally-validated,
build-ready design — leaving Day 3 as pure, piece-by-piece implementation.
