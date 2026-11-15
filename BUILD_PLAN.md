# ResumeGuard — Build Plan (rule-based v1)

> **Status: engineering plan, pre-implementation.** This resolves the open technical
> decisions from `ROUGH_SCOPE.md` §12 now that (a) we've chosen a **rule-based** approach
> and (b) we have real data: 300 scored resumes, the phrasing taxonomy, and the confirmed
> Affinda v1 schema. **No code is written yet.** This document is the thing we review and
> agree on before building.

Companion docs: `ROUGH_SCOPE.md` (product scope), `DAY-2 - Planning/experiments/findings/LIST-A_RESULTS.md`
(the three gaps, validated), `DAY-2 - Planning/experiments/findings/LIST-B_PARSER_DEFECTS.md` (separate
parser-bug log), `DAY-2 - Planning/taxonomy/` (phrasing matrices = our rule source).

---

## 0. Decisions locked by the human (Sprint-2 sign-off)

*Running record of what's been explicitly approved. Only items here are settled.*

- **D1 — Module structure — LOCKED.** Four modules, **each its own blob**: (1) Skill
  Claim Checker, (2) Education Status Checker, (3) Certification Validity Checker,
  (4) Employment-Date Checker. Modules 2 and 3 **share an internal, invisible
  status-detection engine** (a code helper; users still see two separate modules with
  their own labels, switches and reports). **v1 ships modules 1–3** (all validated on the
  300 resumes). **Module 4 (dates) is a fast-follow** — it works on dates not words, so it
  can't share the engine, and it has no experiment set yet (needs its own taxonomy + 100
  resumes first).

- **D2 — Annotation shape — LOCKED.** Separate parallel **`resumeGuard` block (Option
  A)**. Affinda's `data` is returned **byte-for-byte unchanged**; our labels live in their
  own block and reference entries by array index. **No inline tags.** A formatter / UI
  layer reads Affinda's output directly and joins our labels to it by index for display.
  **Field names (LOCKED):** each annotation = `{ entryIndex, entity, status, confidence,
  evidence:{text, rawTextSpan} }`. `entryIndex` = slot in Affinda's source array;
  `entity` = echo of the skill/degree/cert name; `status` = our verdict (D4 vocab).
  (Affinda's own input keys — `name`, `qualification`, etc. — are read under their real
  names and never renamed.)

- **D3 — Evidence format — LOCKED.** Every label carries **both** the quoted snippet
  **and** the character offsets into `rawText` (`{text, rawTextSpan}`). Snippet for people,
  offsets so a UI can highlight the exact source sentence. If an entity can't be located in
  `rawText`, emit snippet only + `confidence: low`, never a fabricated span.

- **D4 — Status vocabularies — LOCKED** (authoritative; supersedes any draft names in
  §6–§7, which get reconciled to these at build time). **The annotation field is named
  `status`** (not `label`) across all three modules.
  - **Skill:** `strong` · `intermediate` · `basic` · `learning` · `lapsed` · `no_experience` ·
    *(plain = no annotation when claimed without a qualifier)*. Ladder: strong → intermediate →
    basic, then special states.
  - **Education:** `completed` · `in_progress` · `expected` · `incomplete`
    (discontinued/withdrawn) · `deferred` (leave/paused) · `not_awarded` · `unknown`.
  - **Certification:** `active` · `expired` · `revoked` · `suspended` · `pending` ·
    `unknown`.

- **D5 — Detection mechanic — LOCKED.** Entity-anchored **3-step** (find entity in rawText →
  read its clause → match cue lexicon), with the **adjacency precision rule** (a negative/weak
  cue only binds to a skill in the same clause with no scope-breaker between). When unsure →
  **stay safe / `unknown`, emit no label** (the "unknown" pile is exactly what a future LLM
  pass would handle). Grammar-parsing and LLM/hybrid noted as future upgrades only.
- **D6 — Grading — LOCKED.** Acceptance = run the tool, compare its labels to known-correct
  answers, count hits/misses/false-alarms + the easy "control" cases + the skill "trap" cases.
  **Data: a NEW blind held-out batch** — generated in a **fresh session that knows nothing of
  our taxonomy or rules** (pure-random résumés) so it's an honest generalization test, not the
  300 we built the rules from (those stay as a quick dev sanity-check only). **Bar: measure
  first, set the pass line after seeing the real numbers** (no guessed thresholds upfront).
  **Batch generation:** a **fresh agent** is briefed on **what** to test (the three label
  types + the List-B defect patterns: dropped skills/credentials, misleading dates) and told
  to make **random, varied** résumés around those targets — but is **NOT** told how we detect
  them, so the test stays blind to our rules.
- **D7 — Deliverable — LOCKED.** Ship **all four** interfaces, built in **3 iterations**,
  each a thin shell around the same core `enrich()` (it never changes):
  **Iter 1 = library + CLI** → **Iter 2 = + HTTP API** → **Iter 3 = + dockerized API.**
  v1 target = **Iteration 1**; iters 2–3 are the committed roadmap.
- **D8 — Tech stack — LOCKED.** Python 3.11+. Layered deps (brain's matcher + each shell
  brings its own):
  - **Brain / matching:** the **`regex` module** (drop-in for stdlib `re`, adds typo-tolerant
    matching like `(expired){e<=1}` — cheap upgrade, took it).
  - **CLI:** **typer** (prettier help, less code).
  - **API:** **FastAPI + uvicorn** (async, auto Swagger docs).
  - **Packaging:** **Docker + docker-compose** (mirrors Affinda's repo).
  - **Tests:** `pytest`, run on the 300 saved responses.
  (Affinda's public repo is Python-dominant + dockerized — the open integrator/client code,
  not the parser core — which only confirms Python as the native fit.) Blueprint in
  **`DESIGN.md`**.

- **D9 — List-B handling — LOCKED.** v1 includes **both** List-B helpers:
  (1) **date caveat** — warn when an incomplete/withdrawn/expected degree still carries a
  graduation-looking end date (cheap, near-free, built on the status label); and
  (2) **missing-entity flag** — scan `rawText` for skills/credentials that have no entry in
  Affinda's output and flag them as possibly-dropped (catches Azure/Spark/Bar-admission).
  Missing-entity flag needs a guarded "what counts as a skill/credential" list to keep
  false-alarms down.

---

## 1. Decision recap

- **Approach: rule-based.** Build and finish the whole product with keyword/pattern rules
  over the extracted entities + `rawText`. Deterministic, explainable, evidence-backed,
  trivial to package. Model-assisted/LLM options are **deferred to a "future additions"
  section** (§11), not v1.
- **Why rule-based is enough for v1:** we already own the exact phrasings (the taxonomy),
  the gaps are lexically signalled ("expired", "withdrawn", "no experience with"), and we
  have a 300-resume harness to prove precision before shipping.

---

## 2. What the product is (one paragraph)

A small adapter that takes an Affinda parse (`data` + the `rawText` inside it) and returns
the **original `data` untouched** plus a **separate** `resumeGuard` object holding the three
restored qualifiers — each as a structured label **with evidence pointing back to the
résumé text**. The caller decides what to do with the labels. It never deletes, moves, or
overwrites anything Affinda returned.

---

## 3. Architecture & data flow

```
Affinda response ─┐
  data{education, certifications, skills, rawText, ...}
  meta{extractionQuality, warnings, ocr, ...}
                  │
                  ▼
         ResumeGuard /enrich
   ┌────────────┬────────────┬────────────┬───────────┐
   ▼            ▼            ▼            ▼
 Module 1     Module 2     Module 3     Module 4
 Skill        Education    Certification Employment-
 Claim        Status       Validity     Date
 Checker      Checker      Checker      Checker
 (skills[])   (education[])(certs[])    (workExp[])
              └── share ───┘            ⬜ fast-follow
               status engine            (dates, not words)
   └────────────┴────────────┴────────────┘
                  ▼
   original data (unchanged)
   + resumeGuard{ skills[], education[], certifications[], findings[] }

Each issue is its own module (own labels / switch / report). Modules 2 & 3 share an
INTERNAL, invisible status-detection engine so the code isn't written twice. v1 = 1–3.
```

- **Pure function / library** at the core: `enrich(data, meta=None, modules=[...]) -> result`.
- **Thin HTTP wrapper**: `POST /enrich`. The library is the real deliverable; the API is a
  convenience.
- **Modules are independent and selectable** (a caller wanting only skill checks passes
  `modules=["skill"]`). Required by `ROUGH_SCOPE.md` §6.

---

## 4. I/O contract  *(resolves ROUGH_SCOPE §12: JSON shape)*

**Decision: a separate parallel object, never inline mutation.** The original `data` is
copied through byte-for-byte; all annotations live under a sibling `resumeGuard` key, linked
back to the original entries by array index.

**Request**
```jsonc
POST /enrich
{
  "data":  { ...the Affinda data object, including rawText... },
  "meta":  { ...optional; used for routing signals only... },
  "modules": ["skill", "education", "certification"]   // optional, default = all
}
```

**Response**
```jsonc
{
  "data": { ...unchanged, exactly as received... },
  "resumeGuard": {
    "version": "1.0",
    "modulesRun": ["skill", "education", "certification"],
    "skills": [
      { "index": 4,                     // -> data.skills[4]
        "name": "SQL (Programming Language)",
        "claimStrength": "denied",       // affirmed|strong|moderate|weak|aspirational|lapsed|denied|unknown
        "confidence": "high",
        "evidence": { "text": "No experience with SQL",
                      "rawTextSpan": [812, 835] } }
    ],
    "education": [
      { "index": 0,
        "completionStatus": "incomplete_withdrawn",
        "dateCaveat": "end date 2020 may read as conferral",   // ties to List-B defect 3
        "evidence": { "text": "withdrawn 2020", "rawTextSpan": [410, 424] } }
    ],
    "certifications": [
      { "index": 0,
        "validityStatus": "expired",
        "evidence": { "text": "expired 2022", "rawTextSpan": [690, 702] } }
    ],
    "findings": [            // flat, human-readable roll-up of everything above
      { "module": "skill", "severity": "warning",
        "message": "Skill 'SQL' is explicitly denied in the résumé but present in skills[]",
        "ref": "skills[4]" }
    ]
  }
}
```

Guarantees: `response.data === request.data` (deep-equal). Every annotation has an
`index`/`ref` and an `evidence` block. Nothing is asserted without a text span.

---

## 5. Evidence representation  *(resolves ROUGH_SCOPE §12: evidence)*

**Decision: both a quoted snippet and character offsets into `rawText`.** Snippet for
humans/demo, offsets for programmatic highlighting. If an entity can't be located in
`rawText` (rare), emit the annotation with `evidence.text` only and
`confidence: "low"`, never a fabricated span.

---

## 6. Module 1 — Skill Claim Checker

**Goal:** label how strongly each extracted skill is claimed; the headline case is detecting
**denied** skills without ever suppressing anything.

**Per skill in `data.skills`:** locate its mention in `rawText` using `skill.text` then
`skill.name`; take the enclosing **clause/line** as the context window; match that window
against ordered lexicons (first strong-negative cue wins):

| claimStrength | cue patterns (illustrative, from taxonomy) |
|---|---|
| `denied` | "no experience with", "not proficient in", "never used", "without any … background", "X: none" |
| `aspirational` | "currently learning", "studying", "learning", "interested in", "keen to learn" |
| `lapsed` | "previously used", "used … years ago", "formerly", "not in recent years" |
| `weak` | "exposure to", "limited/brief exposure", "familiar with", "basic", "some" |
| `moderate` | "working knowledge", "hands-on", "comfortable with" |
| `strong` | "expert", "advanced", "proficient", "strong", "N+ years", "solid" |
| `affirmed` | default when the skill is present with no qualifier |

**Scoped exclusion** ("X, but not Y" / "X (not Y)" / "never used Y"): the negative cue binds
to **Y only**; X stays affirmed.

**Precision safeguards (this is the number that decides shippability — distractor set):**
- A negative/weak cue only applies to a skill when the **skill token is inside the same
  clause and adjacent** to the cue (proximity + boundary). So "No experience with Java;
  expert in Spark" → Java `denied`, Spark `strong`. Never let one negation color the whole
  line.
- **Never remove or rewrite** a skill. Only add a label. Suppression is the caller's choice.
- `cert_vs_use` ("not certified in X, but use X daily") → X stays affirmed (certification
  denial ≠ skill denial).

**Known v1 limits:** can't restore skills Affinda dropped (List-B defect 1 — Azure/Spark);
can optionally emit a *low-confidence* "possible missing skill" finding when a skill-looking
token in `rawText` has no `skills[]` entry, but that's a flag, not an extraction.

---

## 7. Module 2 — Qualification Status Checker (education + certifications)

Two sub-checkers sharing the locate-in-rawText + lexicon machinery.

**2a. Education completion status** — per `data.education` entry:

| completionStatus | cue patterns |
|---|---|
| `in_progress` | "currently enrolled", "in progress", "pursuing", "ongoing", "candidate for", `dateRange.end.current` |
| `expected` | "expected", "anticipated", "graduating", "due" + future year |
| `incomplete_discontinued` | "discontinued", "incomplete", "did not complete", "left before finishing", "unfinished", "partial" |
| `withdrawn` | "withdrawn", "withdrew", "left the program" |
| `not_awarded` | "not awarded", "no degree conferred", "requirements not met", "exams not passed" |
| `deferred` | "deferred", "on academic leave", "study break", "enrolment suspended" |
| `abd` | "ABD", "all but dissertation", "dissertation pending", "comprehensive exams passed" |
| `completed` | "graduated", "conferred", or a terminal past date with no other cue |
| `unknown` | no cue, no date |

- **Date caveat (links List A ↔ List B):** when status ∈ {withdrawn, incomplete, not_awarded,
  expected} *and* `dateRange.end` is set, add `dateCaveat` noting the end date may misread as
  a conferral (this is List-B defect 3, surfaced non-destructively).

**2b. Certification validity** — per `data.certifications` entry (remember: certificate-level
*education* quals are re-emitted here by Affinda, per the docs, so this is the right place):

| validityStatus | cue patterns |
|---|---|
| `active` | "active", "current", "in good standing", "valid", "valid through/until" + future |
| `renewed` | "renewed", "recertified" |
| `expired` | "expired", "lapsed", "no longer valid" |
| `revoked` | "revoked", "withdrawn by issuer", "licence revoked" |
| `suspended` | "suspended", "under suspension" |
| `pending` | "scheduled", "pending", "awaiting results", "candidate" |
| `failed` | "did not pass", "unsuccessful", "attempted" |
| `unknown` | name + date only |

- `pending` / `failed`: label as **not-held**, do not assert the person holds it (matches the
  taxonomy's "omit OR flag" acceptable behaviour).

---

## 8. Entity ↔ rawText alignment (shared helper, the main engineering risk)

A single helper locates an extracted entity's text in `rawText` and returns the context
window + span. Strategy, in order: exact substring of `skill.text` / `qualification` /
`cert.name` → normalized (strip punctuation/case, drop Affinda's trailing "." and
parenthetical normalizations like "(Programming Language)") → token-overlap fuzzy match. On
no match: annotate with `confidence: "low"`, snippet only, no span. This helper is built and
unit-tested **first**, because every module depends on it.

---

## 9. Evaluation plan & acceptance gates  *(the 300 are our harness)*

Reuse the Day-2 setup: run `enrich()` on each stored Affinda response in
`DAY-2 - Planning/experiments/*/results/`, compare the emitted label to the ground-truth
`expected_*` for that row, and roll up with a scorer modelled on `score_experiments.py`.

Per module we report **precision, recall, controls-pass, and (skills) distractor-precision**.
Proposed v1 acceptance gates (tune on review):

| Module | Gate |
|---|---|
| Skill | controls (expert/proficient) ≥ 95% kept as affirmed; denied recall ≥ 80%; **distractor precision = 100%** (never mislabel the affirmed skill) |
| Education | completed controls 100% `completed`; withdrawn/expected/in_progress recall ≥ 85% |
| Certification | valid controls 100% `active`; expired/revoked/suspended recall ≥ 85% |

A module ships only if it clears its gate on the common/very-common realism rows without
tripping controls.

---

## 10. Scope boundary: Problem D (employment dates)

`ROUGH_SCOPE.md` lists a 4th problem (fabricated open-ended end dates) and a 3rd module. It
has **no taxonomy and no resume set yet**, and it's a different shape (comparing dates vs
rawText, not lexical status). **Decision for this plan: v1 = the two qualifier modules
(skill + qualification-status).** Problem D is a fast-follow: if we want it in v1, the
prerequisite is a date taxonomy + 100 resumes first (same method as the other three).

---

## 11. Future additions (explicitly not v1)

- **Hybrid / LLM fallback** for ambiguous or unseen phrasings and non-English cues (e.g.
  "caducado") — the rules give us the baseline to measure any such addition against.
- **Dropped-entity recovery** (beyond flagging) for List-B defect 1/2.
- Problem-D employment-date module.
- Confidence as a numeric score rather than high/low.

---

## 12. Packaging *(resolves ROUGH_SCOPE §12: packaging)*

Pure-Python library + a thin FastAPI (or Flask) `/enrich` app, Dockerised. No model
dependency → tiny image. `docker run -p … resumeguard` serves `/enrich`; the library is
importable for the eval harness and the demo.

---

## 13. Proposed build sequence (once this plan is agreed)

1. **Foundation:** I/O contract + deep-copy passthrough + the rawText alignment helper (§8) + eval-harness wiring. *(no detection yet, but testable)*
2. **Module 1 (Skill):** lexicons + precision safeguards → score against the 100 skill resumes, hit the distractor gate.
3. **Module 2 (Qualification status):** education + certification sub-checkers → score against the 200.
4. **API + Docker + demo** (original vs enriched, side by side) + docs.

Each step produces a number before the next starts.

---

## 14. Open questions for review (before any code)

1. v1 = two modules (skill + qualification-status), with Problem-D as a fast-follow — agreed?
2. Annotation shape: parallel `resumeGuard` object (§4) — agreed, or do you want inline
   `__resumeGuard` on each entry instead?
3. Acceptance gates in §9 — right bar, too strict, too loose?
4. Output: library + HTTP API + Docker — or is the library alone enough for the demo?
