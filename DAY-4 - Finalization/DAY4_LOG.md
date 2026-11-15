# Day 4 — Finalization, Testing & Handover Prep

**Main achievement:** turned the working engine into a finished, self-contained,
scrutiny-proof product repo (`affinda-resumeenricher/`) with delivery interfaces, a full
before/after evaluation on 300 résumés, lean visual docs, and a clean split from the
research/proof material. Renamed ResumeGuard → **Affinda Resume Enricher**.

Worked as two 1.5-hour sprints, then a long finalization/testing pass.

---

## Sprint 1 — expose the engine + understand the flow

- **Flow understanding doc** (a debugger-on-paper): steps a real résumé through
  `enrich()` with real values, shows `rawText` is never mutated (clean-copy + index-map
  round-trip), the for-loops/methods inline, the no-match fallback, and a worked edge
  case. Clarified the **three dials**: status (rules) · severity (fixed lookup) ·
  confidence (located?).
- **Delivery layer built + tested green** (`resume_enricher/delivery/`):
  - `cli.py` (typer): `python -m resume_enricher.delivery.cli FILE [--summary|--enrichment-only]`, bad JSON → exit 2.
  - `api.py` (FastAPI): `GET /health`, `POST /enrich` → EnrichedJSON, bad shape → 422.
  - `docker/`: Dockerfile + compose (config validates; no daemon in this env).
  - Verified the engine stays **pure-stdlib** (no typer/fastapi leak on import).
  - Added `requirements.txt` + `examples/sample_affinda.json`.

## Sprint 2 — test the system & build the before/after case

- **Reproducible eval harness** (`eval/run_eval.py`) over 300 Affinda responses + ground
  truth, with a documented ground-truth→our-vocab mapping and multi-item rows excluded.
- **Bug #1 found & fixed (locator):** the finder treated em-dashes/bullets as clause
  ends, cutting off qualifiers after a dash (`CISSP — expired 2022`). Fix: a separate
  `STATUS_BOUNDARIES` set for education/certification (skills keep the dash). **Lifted
  edu/cert recall from ~30% → ~76–88%.**

## Finalization & testing pass

- **Renamed** ResumeGuard → **Affinda Resume Enricher** (package `resumeguard` →
  `resume_enricher`); "enricher" is accurate (non-destructive, stays enrichment in v2).
- **Self-contained corpus:** `eval/build_dataset.py` bundles all 300 résumés + ground
  truth into one `eval/data/all_resumes.json` (1.1 MB); `run_eval.py` reads it, so the
  repo evaluates itself with no external dependency.
- **Repo split:** product = `affinda-resumeenricher/`; process/proof = this project root
  (DAY-1…4, taxonomy, experiments, planning docs). `.gitignore` added to the product.
- **Doc diet + readability rewrite:** cut ~25 docs down to a lean set and moved the rest
  to the process side (`archived-product-docs/`). Rewrote the survivors for the hardest
  reader: **Mermaid flow diagrams** (render on GitHub), ASCII boxes, short sentences,
  airy layout, **no em-dashes** in prose. Final product docs = **4**:
  - `README.md` — front door (problem, what it adds, how it works, results, run, map).
  - `docs/HOW_IT_WORKS.md` — the mechanism + one worked trace.
  - `docs/DECISIONS.md` — every choice as Do/Why/Instead + journey + roadmap.
  - `docs/REFERENCE.md` — 4 audit answers: is this already in Affinda? / the Affinda bugs
    we found (List B) / the full output contract / honest limits.
- **Results made vivid:** `results_table.md` now shows, per résumé,
  `what the candidate wrote → what Affinda returned → what we added` (warnings first,
  dropped items shown honestly). `REPORT.md` opens with a "see it in action" before/after.
- **Bug #2 found & fixed (eval harness), caught by the user:** the table said
  "AWS (no strength)" then "Affinda dropped it" — a contradiction. Root cause: the
  harness matched the ground-truth name "AWS" against Affinda's **renamed** entity
  "Amazon Web Services", and missed. (Affinda keeps the original wording in a `text`
  field; our *enricher* already uses it and had enriched AWS correctly as `strong`.) Fix:
  match by Affinda item **index** using name + `text`; the table now shows the real name
  Affinda returned. **Lesson: Affinda renames entities — match on the original `text`.**

---

## Final numbers (real, re-runnable, after both fixes)

| Dimension | Caught (recall) | Control precision | Dropped by Affinda (real) |
|---|---|---|---|
| Skill strength | **46/52 (88%)** + traps 6/6 | 23/23 (100%) | 11 (Azure/Tableau/Spark) |
| Education completion | **54/71 (76%)** | 13/13 (100%) | 10 |
| Certificate validity | **42/48 (88%)** | 29/29 (100%) | 7 |

**Zero false accusations across all 300.** Throughput ~0.8–1 ms/résumé (~1,000+/sec,
single-thread) — a sanity footnote, not a load test. 34 unit tests green.

---

## Handover state (for the Day-5 audit)

- Product repo is self-contained and runnable:
  `pip install -r requirements.txt` → `python main.py` / `python -m unittest discover -s tests` / `python eval/run_eval.py`.
- **Still to do:** push both repos to GitHub (`affinda-resumeenricher` +
  `affinda-resumeenricher-process`), after the user reviews the docs and picks
  private/public. A **fresh blind test set** (real Affinda JSON) will be supplied later
  and scored by the same harness.
- Process repo still holds the old names (DESIGN.md, old DECISIONS.md) as history,
  intentionally left.
