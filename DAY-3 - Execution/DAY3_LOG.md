# DAY 3 — Execution — Log (2026-11-14)

**Theme:** Execution. **Goal for today:** finish approving the `DESIGN.md` walkthrough
(piece by piece), then start building per the DESIGN §11 build order.

> **Phase:** Execution.  **Target deliverable:** the working **ResumeGuard enricher** (library
> + CLI, iter 1) built from the approved design. *(In progress.)*

> Day folders relabelled today: **DAY-1 → Ideation**, **DAY-2 → Planning**, **DAY-3 →
> Execution**. Path references in `BUILD_PLAN.md` and `DESIGN.md` updated to the new
> `DAY-2 - Planning/...` paths.

---

## Design walkthrough — pieces approved today

Continuing the dumbed-down, one-piece-at-a-time read of `DESIGN.md` (Pieces 1–3 were done
on Day 2). All decisions also recorded in **`DECISIONS.md`** (new running decision log,
created today, with the options considered for each).

- **Piece 4 — Locator (`shared/locator.py`).** APPROVED.
  - Decision: **Option B** — fully clean the rawText (lowercase + collapse whitespace + strip
    punctuation) to catch messy matches ("S Q L", line breaks), and keep a **per-char index
    map** to translate hits back to original offsets so evidence highlights stay exact.
    (Option A = gentle length-preserving clean, rejected: simpler but misses messy matches.)
  - `DESIGN.md §4` rewritten: `normalize_mapped()` returns `(cleaned_text, idxmap)`.

- **Piece 5 — Rulebook (`_rules.py` per module).** APPROVED.
  - Decision: **fuzzy matching on "killer" cues only** (skill `no_experience`, edu
    `incomplete`/`not_awarded`, cert `expired`/`revoked`/`suspended`) — tagged `# fuzzy` in
    the lists; soft/positive cues matched exactly to avoid false alarms.
  - Decision: education **`expected` only fires with a FUTURE year** present in the clause.
  - Reaffirmed: lists ordered strongest-first, **first match wins**.
  - Also explained why the rulebook stays SMALL: we don't regex entity *names* (Affinda
    already extracted those — the locator just finds them); we only encode the ~40 closed-set
    *qualifier phrases*, reused for every entity. Synonyms grown from test evidence, not
    imagination. Unmatched → stay quiet, never false-accuse.

- **Piece 6 — Skill checker + precision guard (`modules/skill/`).** APPROVED.
  - Decision: precision window = **≤ 6 tokens** between cue and skill (starting point, to
    tune on the test batch).
  - Decision: **research-backed WALL list** (scope breakers) added to `DESIGN.md §6`:
    - hard punctuation walls: `;` `.` newline `|` `—` `–` `/` `•` bullets/dashes
    - contrast/concession walls: but, yet, however, though, although, whereas, while,
      nevertheless, nonetheless, except, aside from, apart from, other than, instead, on the
      other hand
    - NOT walls (keep one scope): and, or, nor, as well as, plus
    - comma = conditional wall (only when a cue follows it, not a plain skill list)
  - (Wall list grounded in discourse-connective research — coordinators / conjunctive
    adverbs / subordinators.)

---

## Piece 7 — Status engine (education + certification) — IN PROGRESS

Two sub-decisions surfaced:

- **Date-only degree (date present, no status words) → labelled `unknown` / stay silent.**
  DECIDED. We won't stamp "completed" on a degree we can't confirm was finished (a withdrawn
  degree can still carry a year). Stay safe.
- **Report scope → FULL ENRICHER.** (First decided problem-catcher, then REVERSED same day.)
  We record a status for EVERY item — a complete mirror of Affinda's list + metadata. Each
  enrichment carries a `severity` tag (`warning`/`info`) so the customer (e.g. SEEK) filters it
  themselves. Rationale: List A item 3 covers the whole strength range (expert…no experience),
  and a data-platform customer prefers complete+predictable data ("easier to filter than to
  recover"). Mechanism: `PROBLEM_STATUSES` → `STATUS_SEVERITY` table (allowed-menu + warning/info
  tag) in `models.py`; `Enrichment` gained a `severity` field; `severity_of()` fails loudly on a
  typo'd status (also settles the allowed-statuses question). Code+docs updated; `DESIGN.md`
  §2d/§6/§7 still describe the old problem-catcher logic — STALE, to be swept.
- **List B bugs:** we can't fix Affinda's parser (closed model) and never edit its data, but our
  enricher FLAGS #1/#2 (missing-entity check) and #3 (date caveat); #4 (JD mis-tagged) is just
  reported, not auto-flagged.

---

## Testing / eval

- **Real-resume precision slice → YES, adding it.** DECIDED. On top of the generated blind
  batch (D6), we'll run a slice of *real* resumes purely to measure **false alarms** (any flag
  on a normal resume is a suspect to inspect; no answer key needed; also stress-tests the
  Option-B messy-text locator). Requires running the real resumes through Affinda first.
  Candidate sources researched: Kaggle LiveCareer set, CareerCorpus (Mendeley), large arXiv
  corpora. **Recall still measured on the generated blind batch.**
- Reminder: `DESIGN.md §8` eval pseudocode still says "reuses the 300" — **STALE**, must be
  fixed to the blind-batch-for-recall + real-slice-for-precision model when we finalise Piece 8.

---

## BUILD SPRINT — full package built end to end ✅

Per the user's instruction ("finish the entire project, end to end… make docs for each file…
I'll audit it next sprint"), the whole package was implemented and is runnable + tested green.

### What exists now (code)
```
resumeguard/
├── main.py                          the run button (baked-in sample + file arg)
└── resumeguard/
    ├── __init__.py                  exposes enrich()
    ├── app/     enrich.py (6-step orchestrator) · registry.py (one feature list)
    ├── modules/ skill/ (__init__ · _classify [precision guard] · _rules)
    │            education/ (__init__ · _rules) · certification/ (__init__ · _rules)
    └── shared/  models.py · validators.py · matching.py · locator.py · status_engine.py
tests/ test_resumeguard.py           34 checks, all green (python -m unittest)
docs/  one .md per .py (see docs/README.md for the map)
```

### Two rough edges from the minimal version — now CLOSED
- **Evidence span alignment (correctness).** Before, `evidence.text` was the matched cue but
  `rawTextSpan` pointed at the *entity*, not the cue — two different things. Fixed: `locator`
  now also returns where the sentence starts; classifiers return the cue's position; a new
  shared helper `models.build_evidence()` lines text + highlight up every time. Verified: for
  all 5 sample items the characters at the span equal the evidence text (e.g. "withdrew" →
  [99,107]).
- **Skill precision guard upgraded to the designed WALL model.** Was a plain comma/semicolon
  split; now cuts the sentence at punctuation **and** joining words (and/but/however/whereas/
  while/though/also/plus) and reads only the skill's own piece. "no experience with SQL but
  expert in Python" → SQL `no_experience`, Python `strong` (guard holds).

### Deliberate v1 boundaries (documented, not forgotten)
- No typo-tolerant ("fuzzy") cue matching yet — exact match only.
- Education/certification read the whole sentence (no precision split) — fine for the normal
  one-item-per-sentence case.
- List-B (Affinda's own bugs) is surfaced via `confidence:"low"` when an item can't be located;
  no separate List-B subsystem was invented beyond that (kept scope tight for the audit).

### Verified
- `python main.py` → SQL `no_experience`/warning, Python `strong`/info, Excel `learning`/warning,
  BSc `incomplete`/warning, AWS `expired`/warning + a 4-line plain-English summary.
- `python -m unittest discover -s tests` → **Ran 34 tests … OK**.

> **Handed to next sprint:** user will audit, rename vocabulary to taste, and "fry and break
> everything." Open design docs still to reconcile against the built code: `DESIGN.md` §2d/§6/§7
> (problem-catcher → full-enricher sweep) and §8 (eval harness: blind-batch recall + real-resume
> precision slice — not built yet, deferred with the eval work).

> Credits are tight — keeping everything lean.
