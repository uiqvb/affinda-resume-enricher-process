# ResumeGuard — Technical Design (v1)  ·  build-ready

> The crystal-clear picture. Everything needed to build tomorrow piece by piece: the tech
> stack, the file tree, every data flow, the if/else core logic, the actual regex rules, the
> validators, and the exact input/output shape. Pairs with `BUILD_PLAN.md` (the locked
> decisions). Nothing here is coded yet — this is the blueprint.

---

## 0. Tech stack (D8) — layered, each shell adds only its own dep

- **Language:** Python 3.11+.
- **Brain / matching:** the **`regex`** module (drop-in for stdlib `re`, same API, adds
  typo-tolerant fuzzy matching e.g. `(expired){e<=1}`). All pseudocode below that says
  `search()` uses `regex`.
- **CLI (iter 1):** **typer**.
- **API (iter 2):** **FastAPI + uvicorn**.
- **Packaging (iter 3):** **Docker + docker-compose**.
- **Tests:** `pytest`, run against the 300 Affinda responses we already saved.
- **Dependency rule:** the brain carries only its matcher; each outer shell (CLI/API/Docker)
  brings its own and nothing else. No spaCy, no LLM in v1 (both are future upgrades).

---

## 1. File tree (the shape)

**Structure = feature-sliced modular monolith.** Four tiers, one-way dependencies only:
`delivery → app → modules → shared`. Features never import each other; a feature's
internals are private (`_`-prefixed); `shared/` knows nothing about any feature.

```
resumeguard/
├── resumeguard/
│   ├── __init__.py                   ← exposes enrich()
│   │
│   ├── shared/                       ═══ SHARED FOUNDATION — reused by every module ═══
│   │   ├── locator.py                ← FLOW B: find an entity in rawText → clause + span
│   │   ├── models.py                 ← data shapes: Evidence, Enrichment, EnrichedJSON
│   │   ├── matching.py               ← regex helpers (fuzzy search, clause scan)
│   │   ├── validators.py             ← input checks + the "original untouched" guarantee
│   │   └── status_engine.py          ← FLOW D engine: generic clause→status (reusable)
│   │
│   ├── modules/                      ═══ FEATURE BLOBS — isolated, self-contained ═══
│   │   ├── skill/
│   │   │   ├── __init__.py            ← PUBLIC door: run(skills, rawText)   [FLOW C]
│   │   │   ├── _classify.py           ← private: the if/else logic
│   │   │   └── _rules.py              ← private: skill cue patterns (SKILL_RULES)
│   │   ├── education/
│   │   │   ├── __init__.py            ← PUBLIC door: run(entries, rawText)  [FLOW D]
│   │   │   ├── _classify.py           ← private: thin wrapper over status_engine
│   │   │   └── _rules.py              ← private: education cue patterns (EDU_RULES)
│   │   └── certification/
│   │       ├── __init__.py            ← PUBLIC door: run(entries, rawText)  [FLOW D]
│   │       ├── _classify.py           ← private: thin wrapper over status_engine
│   │       └── _rules.py              ← private: certification cue patterns (CERT_RULES)
│   │
│   ├── app/                         ═══ ASSEMBLY — wires the modules together ═══
│   │   ├── enrich.py                 ← FLOW A: orchestrator (calls modules, builds output)
│   │   └── registry.py               ← the list of active modules (1 line = add a module)
│   │
│   └── delivery/                    ═══ INTERFACES — ways to run it ═══
│       ├── cli.py                    ← SHELL 1 (iter 1): typer command
│       ├── api.py                    ← SHELL 2 (iter 2): FastAPI endpoint
│       └── docker/                   ← SHELL 3 (iter 3)
│           ├── Dockerfile
│           └── docker-compose.yml
│
├── tests/
│   ├── test_locator.py
│   ├── test_skill.py
│   ├── test_education.py
│   ├── test_certification.py
│   ├── test_boundaries.py            ← enforces one-way deps (the only "discipline" test)
│   └── eval_harness.py               ← FLOW E: run the blind batch, score vs ground truth (D6)
├── demo/
│   └── before_after.py               ← prints Affinda output vs enriched, side by side
├── README.md
└── pyproject.toml                    ← package metadata + deps (regex, typer, fastapi, uvicorn)
```

**Boundary rule (the thing that keeps it clean):** one small `test_boundaries.py` asserts the
import direction — a feature may import `shared/`, nothing else; `shared/` imports no feature.
No framework, no base classes, no plugin machinery — just a convention plus that one test.

Build order tomorrow = foundation first, shells after. Core: `models` → `locator` /
`matching` → `status_engine` → the 3 feature `_rules`/`_classify` → `app/enrich` +
`registry` → `eval_harness` → `demo`. Then delivery by iteration: `cli.py` (iter 1) →
`api.py` (iter 2) → `docker/` (iter 3). **V2 = add a feature** (e.g. employment-date): new
`modules/<feature>/` folder + one line in `registry.py`; `app/`, `shared/`, delivery untouched.

---

## 2. The shape of the data (input → internal → output)

### 2a. Input (what Affinda gives us)
```python
affinda = {
  "data": { "education": [...], "certifications": [...], "skills": [...],
            "rawText": "....", ... },     # we read these 4; everything else passes through
  "meta": { ... }                          # optional; routing signals only
}
```

### 2b. Internal shapes (`models.py`)
```python
@dataclass
class Evidence:
    text: str                  # the quoted snippet, e.g. "No experience with SQL"
    rawTextSpan: tuple | None  # (start, end) char offsets, or None if not located

@dataclass
class Enrichment:
    entryIndex: int            # which ORIGINAL item this is about -> data.skills[entryIndex]
    entity: str                # echo of the skill/degree/cert name (human cross-check)
    status: str                # the chosen status, e.g. "no_experience" / "expired" / "strong" / "plain"
    confidence: str            # "high" | "low"  — how sure we are of the status
    severity: str              # "warning" | "info"  — for the customer to filter
    evidence: Evidence

@dataclass
class EnrichedJSON:
    originalJSON: dict          # Affinda's WHOLE response, DEEP-COPIED, never mutated
    enrichmentJSON: dict        # { version, checksRun, skills[], education[],
                               #   certifications[], summary[] }
```

### 2c. Output (what we return) — original + our enrichments (D2)
```jsonc
{
  "originalJSON": { ...Affinda's whole response, unchanged... },
  "enrichmentJSON": {
    "version": "1.0",
    "checksRun": ["skill", "education", "certification"],
    "skills":        [ {entryIndex, entity, status, confidence, severity, evidence:{text, rawTextSpan}} ],
    "education":     [ {entryIndex, entity, status, confidence, severity, evidence} ],
    "certifications":[ {entryIndex, entity, status, confidence, severity, evidence} ],
    "summary":       [ "plain-English lines, one per warning" ]   // human roll-up
  }
}
```

### 2d. Full-enricher mode (decided 2026-11-14, supersedes problem-catcher)
The tool is a full **enricher**: it records a status for **EVERY** item — a **complete mirror**
of Affinda's list with added context. Nothing is dropped. Each enrichment carries a `severity`:
`warning` (worth a recruiter's attention) or `info` (fine / neutral). Items with no signal are
still listed (`plain` for skills, `unknown` for edu/cert — both `info`). Rationale: a SEEK-type
data customer prefers complete, predictable data and filters it themselves ("easier to filter
than to recover"); List A item 3 covers the whole strength range (expert … no experience).

```python
# One table: KEYS = the allowed-status menu; VALUES = the severity tag.
STATUS_SEVERITY = {
  "skill": {"no_experience":"warning","learning":"warning","lapsed":"warning","basic":"warning",
            "intermediate":"info","strong":"info","plain":"info"},
  "education": {"in_progress":"warning","expected":"warning","incomplete":"warning",
                "deferred":"warning","not_awarded":"warning","completed":"info","unknown":"info"},
  "certification": {"expired":"warning","revoked":"warning","suspended":"warning","pending":"warning",
                    "active":"info","unknown":"info"},
}   # severity_of(kind, status) raises if status is not a key (catches typos loudly).
```

---

## 3. FLOW A — top-level `enrich()`  (`app/enrich.py`)

**Job:** take Affinda's response, run the chosen modules, return originalJSON + enrichmentJSON.

```
# app/registry.py  — the ONE place features are registered.
#   name          ->  (run function,        Affinda input key,  our output key)
REGISTRY = {
  "skill":         (skill.run,         "skills",         "skills"),
  "education":     (education.run,      "education",      "education"),
  "certification": (certification.run, "certifications", "certifications"),
}   # V2: add a feature = ONE line here (e.g. "employment_date": (...))

# app/enrich.py
enrich(affinda, modules=REGISTRY.keys()):
    validate_input(affinda)                       # shared/validators.py
    original = deep_copy(affinda)                  # deep-copy the WHOLE original
    data     = original.get("data", {})            # we read items from here (never write)
    rawText  = data.get("rawText", "")
    out = { version:"1.0", checksRun:list(modules),
            skills:[], education:[], certifications:[], summary:[] }

    for name in modules:                          # loop, not hardcoded ifs
        run_fn, input_key, output_key = REGISTRY[name]
        out[output_key] = run_fn(data.get(input_key, []), rawText)   # ALL items, severity-stamped

    out["summary"] = build_summary(out)           # roll the WARNINGS up to plain-English lines
    ensure_untouched(affinda, original)           # GUARANTEE: original untouched
    return { "originalJSON": original, "enrichmentJSON": out }
```

Key points: features are selectable, driven by the registry (so adding one never edits this
function); `ensure_untouched` is the contract that we changed nothing; every feature's `run()`
returns a list of `Enrichment` dicts — **one per item** (full mirror), each already carrying its
`severity`. Note: `data` here is read from the frozen `original`, so `enrich` never aliases
Affinda's live object.

---

## 4. FLOW B — the locator (shared)  (`shared/locator.py`)

**Job:** given an entity's text and the full rawText, find where it is and return the
surrounding clause + the character span. Every module depends on this.

**Normalization = FULL clean + index map (Option B, chosen 2026-11-14).** We fully clean the
rawText to maximise matches (lowercase, collapse runs of whitespace, strip punctuation — so
`"S Q L"`, line-break splits and stray punctuation still match). Because full cleaning changes
string length, we keep a per-char **index map** from each cleaned position back to its original
position, and translate every hit back through it before building the span/clause. Highlights
therefore stay exact even though we searched the squished text.

```
locate(entity_text, rawText):
    needle        = normalize(entity_text)     # lowercase, collapse ws, strip punctuation,
                                               #   drop Affinda extras "(Programming Language)", trailing "."
    hay, idxmap   = normalize_mapped(rawText)  # cleaned text + map[clean_pos] -> orig_pos
    cpos = hay.find(needle)                    # 1) exact (on cleaned text)
    if cpos == -1:
        cpos = fuzzy_token_find(hay, needle)   # 2) token-overlap fallback
    if cpos == -1:
        return None, None                      # not found -> caller emits confidence:low, no span

    start = idxmap[cpos]                        # translate BACK to original offsets
    end   = idxmap[cpos + len(needle) - 1] + 1 #   (so span indexes real rawText)
    span   = (start, end)
    clause = clause_around(rawText, start)     # 3) widen in the ORIGINAL text to boundaries
                                               #    (split on . ; \n | — bullet marks)
    return clause, span
```

`normalize_mapped` returns the cleaned string plus `idxmap`, a list where `idxmap[i]` is the
original-rawText index of the i-th cleaned char. `clause_around` = expand left/right from the
hit (in the original rawText) until a boundary char (`.`, `;`, newline, `|`, `—`, bullet) or a
max window (~120 chars) — this clause is what the lexicon scans.

---

## 5. The regex rules — the actual patterns

Each feature keeps its own patterns in its own private `modules/<feature>/_rules.py`
(`skill/_rules.py` holds `SKILL_RULES`, `education/_rules.py` holds `EDU_RULES`,
`certification/_rules.py` holds `CERT_RULES`). There is no shared lexicon file — rules live
with the feature they belong to. Each status owns an ordered list of compiled regexes. **Order matters: first match wins**,
and the lists are ordered strongest-signal-first so a clear negation beats a weak cue.
All matched case-insensitively against the located **clause**.

**Fuzzy matching = KILLER cues only (decided 2026-11-14).** Typo-tolerance (`regex`'s
`{e<=1}`) is applied ONLY to the hard, decisive cues — the ones that flip a claim from
good→bad: skill `no_experience` negations, education `incomplete`/`not_awarded`, and cert
`expired`/`revoked`/`suspended`. Soft/positive cues (basic, intermediate, strong, learning,
completed, active, pending, …) are matched **exactly** — fuzzing them invites false alarms.
Each killer pattern below is tagged `# fuzzy`; everything else is exact.

**"expected" needs a FUTURE year (decided 2026-11-14).** The education `expected` status only
fires when the clause also contains a year greater than the current year; "expected" with no
year, or with a past year, does NOT count as expected (enforced in §7 `classify_status`).

### 5a. Skill cue rules (checked in THIS order)
```python
SKILL_RULES = [            # (label, patterns)
 ("no_experience",[r"\bno\s+(experience|exposure|background|knowledge)\b",   # fuzzy
                   r"\bwithout\s+(any\s+)?\w*\s*(experience|background)\b",  # fuzzy
                   r"\bnot\s+(proficient|experienced|familiar)\b",          # fuzzy
                   r"\bnever\s+(used|worked with|touched)\b",               # fuzzy
                   r":\s*none\b"]),                                         # fuzzy
 ("learning",     [r"\b(currently\s+)?(learning|studying|teaching myself)\b",
                   r"\binterested in\b", r"\bkeen to learn\b", r"\baspir(e|ing)\b"]),
 ("lapsed",       [r"\b(previously|formerly|used to)\b", r"\byears ago\b",
                   r"\bnot in recent years\b", r"\bno longer (use|work)\b"]),
 ("basic",        [r"\bbasic\b", r"\bfamiliar with\b", r"\bsome\b", r"\blimited\b",
                   r"\bbrief\b", r"\bexposure to\b", r"\bbeginner\b", r"\bentry[- ]level\b"]),
 ("intermediate", [r"\bworking knowledge\b", r"\bhands[- ]on\b", r"\bcomfortable with\b",
                   r"\bmoderate\b", r"\bsolid\b"]),
 ("strong",       [r"\bexpert\b", r"\badvanced\b", r"\bextensive\b", r"\bstrong\b",
                   r"\bproficient\b", r"\bseasoned\b", r"\b\d+\+?\s*years?\b",
                   r"\bdeep (experience|expertise)\b"]),
]   # no rule matches -> status = "plain" (still emitted, severity "info")
```

### 5b. Education cue rules
```python
EDU_RULES = [
 ("in_progress",[r"\bcurrently enrolled\b", r"\bin progress\b", r"\bongoing\b",
                 r"\bpursuing\b", r"\bstudying towards\b", r"\bcandidate for\b",
                 r"\benrolled\b", r"\bABD\b", r"\ball but dissertation\b"]),
 ("expected",   [r"\bexpected\b", r"\banticipated\b", r"\bgraduating\b", r"\bdue\b",
                 r"\bprojected\b"]),      # + a FUTURE year present in the clause
 ("incomplete", [r"\bdiscontinued\b", r"\bincomplete\b", r"\bdid not complete\b",   # fuzzy
                 r"\bleft before finishing\b", r"\bunfinished\b", r"\bpartial\b",
                 r"\bdropped out\b", r"\bwithdr(ew|awn)\b"]),
 ("deferred",   [r"\bdeferred\b", r"\bon (academic )?leave\b", r"\bstudy break\b",
                 r"\benrol(l)?ment (suspended|paused)\b", r"\bintermission\b"]),
 ("not_awarded",[r"\bnot awarded\b", r"\bno degree (conferred|awarded)\b",   # fuzzy
                 r"\brequirements not met\b", r"\bexams not passed\b"]),
 ("completed",  [r"\bgraduated\b", r"\bconferred\b", r"\bawarded\b", r"\bcompleted\b",
                 r"\bearned\b"]),        # OR: terminal past date present & no other cue
]   # nothing matches & no date -> "unknown"
```

### 5c. Certification cue rules
```python
CERT_RULES = [
 ("expired",   [r"\bexpired\b", r"\blapsed\b", r"\bno longer valid\b", r"\bout of date\b"]),  # fuzzy
 ("revoked",   [r"\brevoked\b", r"\brescinded\b", r"\bwithdrawn by (the )?issuer\b",       # fuzzy
                r"\bstruck off\b", r"\bcancelled by\b"]),
 ("suspended", [r"\bsuspended\b", r"\bunder suspension\b", r"\btemporarily (inactive|withdrawn)\b"]),  # fuzzy
 ("pending",   [r"\bpending\b", r"\bscheduled\b", r"\bawaiting\b", r"\bcandidate\b",
                r"\bregistered for\b", r"\bsitting\b", r"\bdid not pass\b",
                r"\bunsuccessful\b", r"\bfailed\b"]),
 ("active",    [r"\bactive\b", r"\bcurrent\b", r"\bin good standing\b", r"\bvalid\b",
                r"\brenewed\b", r"\brecertified\b"]),   # "valid until <future>" also active
]   # name + date only, nothing matches -> "unknown"
```

---

## 6. FLOW C — Skill Claim Checker  (`modules/skill/`: `__init__.run` + `_classify` + `_rules`)

```
run(skills, rawText):                        # full enricher: ONE Enrichment per skill
    out = []
    for i, s in enumerate(skills):
        name = s.get("name")
        clause, span = locate(s.get("text") or name, rawText)
        if clause is None:
            status, matched = "plain", None  # couldn't locate it -> no signal (info)
        else:
            status, matched = classify_skill(clause, s, rawText)
        conf = "high" if span else "low"
        out.append(Enrichment(i, name, status, conf,
                              severity_of("skill", status),      # warning | info
                              Evidence(matched or name, span)))
    return out                               # every skill mirrored, each severity-stamped
```

### classify_skill — the if/else core + the PRECISION rule
```
classify_skill(clause, skill, rawText):
    skill_pos = position of the skill token inside the clause
    for (status, patterns) in SKILL_RULES:       # ordered: no_experience > learning > ... > strong
        for p in patterns:
            m = search(p, clause)
            if m and is_bound_to_skill(m, skill_pos, clause):   # <-- PRECISION GUARD
                return status, m.group(0)
    return "plain", None

is_bound_to_skill(match, skill_pos, clause):
    # the cue must apply to THIS skill, not a neighbour. Three gates, all must hold:
    #   1. same_clause            — cue and skill in the located clause
    #   2. within_token_window    — <= 6 tokens between cue and skill (LOCKED 2026-11-14)
    #   3. no WALL between them    — no scope-breaker sits between the cue and the skill
    # Handles "No experience with Java; expert in Spark":
    #   - for Java: "no experience" is adjacent, no wall -> no_experience
    #   - for Spark: a ';' WALL separates it from "no experience" -> that cue NOT bound,
    #                "expert" is -> strong
    return (same_clause and within_token_window and no_wall_between)

# WALL_WORDS — scope breakers (grounded in discourse-connective research, 2026-11-14).
# A wall between the cue and the skill means the cue does NOT reach the skill.
WALL = {
  # --- hard punctuation walls (always break scope) ---
  "punct":   [";", ".", "\n", "|", "—", "–", "/", "•", "·", "*", "- "],  # bullets/dashes/newlines
  # --- contrastive / concessive connectives (break scope) ---
  "contrast":[ r"\bbut\b", r"\byet\b", r"\bhowever\b", r"\bthough\b",
               r"\balthough\b", r"\bwhereas\b", r"\bwhile\b", r"\bnevertheless\b",
               r"\bnonetheless\b", r"\bexcept\b", r"\baside from\b", r"\bapart from\b",
               r"\bother than\b", r"\binstead\b", r"\bhaving said that\b",
               r"\bon the other hand\b" ],
  # --- NOT walls: additive coordinators keep one scope ("no experience and no interest in X") ---
  #     "and", "or", "nor", "as well as", "plus"  -> handled by the token window only.
  # --- comma: conditional wall (decided 2026-11-14) ---
  #     a "," is a wall ONLY when a cue word follows it (", but no experience"),
  #     NOT when it merely separates a plain skill list ("Python, Java, SQL").
}
```

Scoped exclusion ("X, but not Y") falls straight out of this: the "but not" sits next to Y,
so Y gets `no_experience` and X keeps its own cue.

---

## 7. FLOW D — Status engine + Education + Certification

The two status modules are thin wrappers over one shared engine (the invisible helper).

### shared/status_engine.py
```
run_status(entries, rawText, RULES, kind):   # full enricher: ONE Enrichment per item
    out = []
    for i, e in enumerate(entries):
        name = e.get("qualification") or e.get("name")
        clause, span = locate(name, rawText)
        if clause is None:
            status, matched = "unknown", None   # couldn't locate it -> no signal (info)
        else:
            status, matched = classify_status(clause, e, RULES, kind)
        out.append(Enrichment(i, name, status, "high" if span else "low",
                              severity_of(kind, status),          # warning | info
                              Evidence(matched or name, span)))
    return out

classify_status(clause, entry, RULES, kind):
    future = clause has a year > current_year
    for (label, patterns) in RULES:
        for p in patterns:
            if search(p, clause):
                if label == "expected" and not future:   # "expected" needs a future year
                    continue
                return label, matched_text
    # no cue matched -> we cannot confirm a status from a bare date.
    # (decided 2026-11-14: never assume a lone graduation/end date means "completed" —
    #  a withdrawn degree can still carry a year. "unknown" is emitted as severity "info".)
    return "unknown", None
```

### modules/education/__init__.py  /  modules/certification/__init__.py
```
# modules/education/__init__.py   (EDU_RULES lives in modules/education/_rules.py)
run(entries, rawText):  return run_status(entries, rawText, EDU_RULES, "education")

# modules/certification/__init__.py   (CERT_RULES lives in modules/certification/_rules.py)
run(entries, rawText):  return run_status(entries, rawText, CERT_RULES, "certification")
```

**Education date caveat (links to List-B defect 3):** inside `run_status`, if the final
status ∈ {incomplete, expected, not_awarded, deferred} AND the entry still has a
`dateRange.end.date`, append a finding: "end date may read as conferral."

---

## 8. FLOW E — eval harness (D6, how we grade it)  (`tests/eval_harness.py`)

Grading runs on **TWO independent sets** (decided per D6 + 2026-11-14):

**(A) RECALL — the fresh blind generated batch** (does it catch the bad stuff?).
A separate agent generates new résumés, told only *what* to test (the 3 status types + the
List-B patterns), never *how* we detect them. We own the ground truth, so we auto-score.
```
for issue in ["education","certification","skill"]:
    responses   = load(f"blind_batch/{issue}/...responses.json")   # NEW, held-out
    groundtruth = load(f"blind_batch/{issue}/ground_truth_{issue}.json")
    for each resume:
        result    = enrich({"data": response.data})      # run OUR tool
        predicted = result.enrichmentJSON[issue] statuses   # full mirror; compare status per item
        expected  = groundtruth[id].expected_*           # the correct answer
        tally(predicted vs expected)                     # correct / miss / wrong
    report recall, controls-pass, distractor-precision
```

**(B) PRECISION — the real-resume slice** (does it stay quiet on normal résumés?).
Real résumés (e.g. Kaggle LiveCareer) parsed through Affinda first; they almost never contain
our target flaws, so **every flag our tool raises is a suspect**. No ground-truth needed —
count flags raised, inspect them, and the false-alarm rate falls straight out.
```
for resume in real_resumes_through_affinda:
    result = enrich(resume)
    for ann in result.enrichmentJSON warnings:           # any WARNING = candidate false alarm
        collect(ann) for human/auto inspection
report false_alarm_rate = wrong_flags / total_entries_seen
```

**The old 300 (`DAY-2 - Planning/experiments/`)** are demoted to a **quick dev sanity-check**
only — handy while coding, NOT the acceptance set. **Bar = measure first, set the pass line
after seeing the real numbers.**

---

## 9. Validators (`shared/validators.py`)

```
validate_input(affinda):
    assert isinstance(affinda, dict) and "data" in affinda
    d = affinda["data"]
    # arrays may be absent OR empty -> treat both as "nothing to do" (schema is sparse)
    for k in ("skills","education","certifications"):
        assert k not in d or isinstance(d[k], list)
    # rawText may be missing -> locator just returns no spans (confidence stays low)

# output guarantee is the assert in enrich(): deepcopy in, compare out == in.
```

Defensive reads everywhere (`.get()`), empty arrays are normal (not errors), missing keys
mean "not found" — exactly matching Affinda's documented sparse-schema contract.

---

## 10. D6 & D7 in plain words

**D6 — How we know it works (grading).** Acceptance runs on a **NEW blind held-out batch**
— fresh résumés generated by a separate agent that is told only **what** to test (the 3
status types + the List-B defect patterns), never **how** we detect them. For each one we
compare the status *our* tool produced to the *correct* status in ground truth, and count:
right / missed / wrong — plus "did any control break?" and "did any distractor trap fail?".
**Bar = measure first, set the pass line after seeing the real numbers.** (The original 300
stay only as a quick dev sanity-check, not the acceptance set.)

**D7 — What we actually hand over (deliverable).** **All four interfaces, shipped over 3
iterations:** iter 1 = importable **library + CLI**; iter 2 = **+ web API**; iter 3 =
**+ dockerized API**. All four are thin doors over the one `enrich()` brain, so each
iteration adds a shell without touching the core. A **demo script** (Affinda vs enriched,
side by side) ships from iter 1.

---

## 11. Tomorrow's build sequence (piece by piece)

1. `shared/models.py` + `shared/validators.py` — the shapes and guards. *(tiny)*
2. `shared/locator.py` + `shared/matching.py` — find entity in rawText + tests. **Build first; everything leans on it.**
3. `shared/status_engine.py` — the generic clause→status engine.
4. `modules/education/` + `modules/certification/` (`_rules` + `__init__.run`) — score the status features.
5. `modules/skill/` (`_rules` + `_classify` with the precision guard) — hit distractor-precision.
6. `app/registry.py` + `app/enrich.py` — wire the orchestrator + the untouched-original assert.
7. `tests/test_boundaries.py` — lock the one-way import rule.
8. `delivery/cli.py` + `demo/before_after.py` + `README.md` — **iter 1 done.**
9. `eval_harness.py` — run the blind batch, report the real numbers.
   *(iter 2: `delivery/api.py` · iter 3: `delivery/docker/`)*

Each step ends with a number or a passing test before the next begins.
