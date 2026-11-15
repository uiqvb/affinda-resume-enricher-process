# Resume Enricher — documentation map

One `.md` here per `.py` in the package, same folder shape. Every doc is written in
plain English + pseudocode (no specific programming language), with worked examples.

## What Resume Enricher is (one paragraph)

Affinda reads a resume and pulls out skills, degrees and certificates — but it drops
the small print. It lists "SQL" even when the resume says *"no experience with SQL"*,
and lists a certificate that actually expired. Resume Enricher reads that same resume text
and **adds the small print back** as a separate block of notes, one per item, each
tagged `warning` or `info`. It **never changes** Affinda's original output.

---

## Context & narrative (read these first)

- [`../README.md`](../README.md) — the front door: why it matters, what it produces, results.
- [`HOW_IT_WORKS.md`](HOW_IT_WORKS.md) — the logic in depth, compact.
- [`FLOW_WALKTHROUGH.md`](FLOW_WALKTHROUGH.md) — a value-by-value debugger trace on a real résumé.
- [`DECISIONS.md`](DECISIONS.md) — every design choice, with the alternatives rejected.
- [`ROADMAP.md`](ROADMAP.md) — where v2 goes.
- [`../eval/results/REPORT.md`](../eval/results/REPORT.md) — the before/after evaluation.

---

## Start here (code docs)

1. [`main.md`](main.md) — the run button; run it, see output in 10 seconds.
2. [`app/enrich.md`](app/enrich.md) — the whole pipeline in six steps.
3. The delivery doors: [`delivery/cli.md`](delivery/cli.md) · [`delivery/api.md`](delivery/api.md) · [`delivery/docker.md`](delivery/docker.md).
4. Then follow the tree below into whichever piece you want to break.

---

## The map (code → doc)

```
resume_enricher/
├── main.py                         ►  main.md              the run button
│
└── resume_enricher/
    ├── __init__.py                 ►  (re-export only: exposes enrich())
    │
    ├── app/                        the pipeline that ties it together
    │   ├── enrich.py               ►  app/enrich.md         the orchestrator (6 steps)
    │   └── registry.py             ►  app/registry.md       the one list of features
    │
    ├── modules/                    one folder per feature (never import each other)
    │   ├── skill/
    │   │   ├── __init__.py         ►  modules/skill/__init__.md     front door: run()
    │   │   ├── _classify.py        ►  modules/skill/_classify.md    the PRECISION GUARD
    │   │   └── _rules.py           ►  modules/skill/_rules.md       skill cue words
    │   ├── education/
    │   │   ├── __init__.py         ►  modules/education/__init__.md front door: run()
    │   │   └── _rules.py           ►  modules/education/_rules.md   degree cue words
    │   └── certification/
    │       ├── __init__.py         ►  modules/certification/__init__.md front door
    │       └── _rules.py           ►  modules/certification/_rules.md cert cue words
    │
    └── shared/                     the foundation everything builds on
        ├── models.py               ►  shared/models.md       the data SHAPES + severity menu + build_evidence
        ├── validators.py           ►  shared/validators.md   the safety guards
        ├── matching.py             ►  shared/matching.md     text cleaning + index map (the "hands")
        ├── locator.py              ►  shared/locator.md      the finder (the "brain")
        └── status_engine.py        ►  shared/status_engine.md shared engine for education + certification

tests/
└── test_resume_enricher.py            ►  tests/test_resume_enricher.md  34 checks, the safety net
```

---

## How the pieces talk (one-way, top to bottom)

```
main.py
   │ calls
   ▼
app/enrich.py  ──reads──►  app/registry.py
   │ runs each feature
   ▼
modules/skill · education · certification          (features never call each other)
   │ every feature leans on
   ▼
shared/  models · validators · matching · locator · status_engine
```

Dependencies only ever point **downward** (`delivery → app → modules → shared`). A
feature can use the shared foundation; the foundation never reaches up into a feature.

---

## The two ideas worth understanding first

- **The precision guard** (skills) — read only the *piece* of a sentence that belongs
  to each skill, so "no experience with SQL, expert in Python" never calls Python
  denied. Full walkthrough: [`modules/skill/_classify.md`](modules/skill/_classify.md).
- **The index map** (highlights) — cleaning the messy resume text changes its length,
  so we keep a translation list that turns a position in the cleaned text back into the
  exact spot in the original. That's what keeps every highlight precise. Walkthrough:
  [`shared/matching.md`](shared/matching.md).

---

## Known limitations (collected, honest)

These are deliberate v1 boundaries, each noted in the relevant doc:

- **No typo tolerance yet** — cue matching is exact; "experiance" won't match. The
  "fuzzy" upgrade is deferred.
- **Education/certification read the whole sentence** (no precision-guard split) —
  fine for one item per sentence, the normal case.
- **Very short, punctuation-heavy skill names** (`C++`, `C#`, `.NET`) clean down to
  short tokens and are easy to confuse; the fuzzy backup is switched off for them.
- Highlights are never *wrong* — at worst the finder picks a different occurrence of
  the same word; the sentence step tolerates that.
