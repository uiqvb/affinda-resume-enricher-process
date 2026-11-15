# Flow Walkthrough — watching the data change, step by step

This doc is a **debugger session on paper.** We take one real resume, press "step",
and watch every important value change as it moves through Resume Enricher — until we can
see, concretely, *what we added that Affinda didn't give us.*

Everything here is **real output** from `python main.py`, not invented.

---

## The one idea to hold onto

> **The resume text (`rawText`) is NEVER changed. It's a fixed ruler.**
> What flows and changes is a chain of *derived* values we build from it —
> a cleaned copy, a position, a sentence, a piece, a status — and at the end we
> map our answer **back onto the original ruler** so the highlight is exact.

So when you ask "how does rawText change?" — it doesn't. But everything we *derive*
from it changes at every step. That derived chain is what this doc follows.

---

## What do we actually ADD? (the whole point)

Affinda hands us a skill like this — just a **bare name, no judgement**:

```json
{ "name": "SQL" }
```

We hand back the **original untouched**, PLUS a brand-new sibling block of our own
judgement about that same skill:

```json
{
  "entryIndex": 0,
  "entity": "SQL",
  "status": "no_experience",     ← what we read in the text
  "confidence": "high",          ← did we actually find it? yes
  "severity": "warning",         ← how much a recruiter should care
  "evidence": {                  ← the proof, highlight-exact
    "text": "no experience",
    "rawTextSpan": [8, 21]
  }
}
```

**That record is the addition.** Affinda said *"this person has SQL."* We add
*"...but the text literally says 'no experience with SQL' — here are the exact words,
at characters 8–21."* We never delete or overwrite Affinda; we **enrich** it with a
parallel block.

And the final package is always this shape:

```
EnrichedJSON = {
  "originalJSON":   <Affinda's response, copied, byte-for-byte unchanged>,
  "enrichmentJSON": <everything WE added — the block above, one per item, + a summary>
}
```

---

## The input we'll step through

```json
{ "data": {
    "skills":         [ {"name":"SQL"}, {"name":"Python"}, {"name":"Excel"} ],
    "education":      [ {"qualification":"BSc Computer Science"} ],
    "certifications": [ {"name":"AWS Certified Solutions Architect"} ],
    "rawText": "Skills: no experience with SQL, expert in Python, learning Excel.
                Education: BSc Computer Science (withdrew 2016).
                Certifications: AWS Certified Solutions Architect (expired 2021)."
} }
```

Notice: the three lists carry **only names**. All the damning context ("no experience",
"withdrew", "expired") is buried in `rawText`. Our whole job is to dig it back out and
attach it to the right item.

---

## Level 1 — the pipeline watch window (`enrich()`)

Six steps. Here's the "watch window" — the key variables after each line runs:

| Step | What runs | Watch window (the value that just appeared) |
|---|---|---|
| 1 | `validate_input(affinda)` | *(no value — just a bouncer; raises if the shape is wrong)* |
| 2 | `original = deep_copy(affinda)` | a **separate** clone; from now on we read the clone, never the input |
| 3 | `raw_text = data["rawText"]` | the 180-char ruler (read-only from here on) |
| 3 | build empty `enrichment` | `{version, checksRun, skills:[], education:[], certifications:[], summary:[]}` |
| 4 | loop the `REGISTRY` | each check fills one list — see Level 2 below |
| 5 | `_build_summary(enrichment)` | one plain line per **warning** |
| 6 | `ensure_untouched(affinda, original)` | proves the clone still equals the input, then returns |

### The real code (the loop that IS the engine)

This is the heart of `app/enrich.py` — the `for` loop in step 4:

```python
names = list(modules) if modules else list(REGISTRY.keys())
# names = ["skill", "education", "certification"]

validate_input(affinda)              # 1. bouncer
original = deep_copy(affinda)        # 2. photocopier
data = original.get("data")
raw_text = data.get("rawText", "")   # 3. the ruler

enrichment = {"version": "1.0", "checksRun": names,
              "skills": [], "education": [], "certifications": [], "summary": []}

for name in names:                                   # 4. run each check
    run_fn, input_key, output_key = REGISTRY[name]   #    unpack the registry row
    enrichment[output_key] = run_fn(data.get(input_key) or [], raw_text)

enrichment["summary"] = _build_summary(enrichment)   # 5. roll up warnings
ensure_untouched(affinda, original)                  # 6. auditor
return {"originalJSON": original, "enrichmentJSON": enrichment}
```

Reading the loop: `REGISTRY["skill"]` is the tuple `(skill.run, "skills", "skills")`.
So the three variables unpack to `run_fn=skill.run`, `input_key="skills"`,
`output_key="skills"`, and the line runs `skill.run(data["skills"], raw_text)` and
stores the list it returns under `enrichment["skills"]`. Next loop pass does the same
for education, then certification. **That one line is the only place real work happens.**

---

## Level 2 — STEP INTO one skill: `"SQL"` through the finder + classifier

This is the debugger core. Every value below is the real dumped state.

### The caller: `skill.run()`'s for-loop (`modules/skill/__init__.py`)

This loop runs once per skill. STEPS 1–8 below are everything that happens for the
**first pass** of this loop, when `skill = {"name": "SQL"}`:

```python
def run(skills, raw_text):
    out = []
    for i, skill in enumerate(skills):              # i=0, skill={"name":"SQL"}
        name = skill.get("name") or ""              # "SQL"
        clause, clause_start, span = locate(skill.get("text") or name, raw_text)   # STEPS 1–5
        if clause is None:
            status, matched, pos = "plain", None, None     # couldn't find it -> stay quiet
        else:
            status, matched, pos = classify_skill(clause, name)   # STEPS 6–7
        out.append(
            Enrichment(
                entryIndex=i,                        # 0
                entity=name,                         # "SQL"
                status=status,                       # "no_experience"
                confidence="high" if span else "low",    # "high"
                severity=severity_of("skill", status),   # table lookup -> "warning"
                evidence=build_evidence(name, matched, pos, clause_start, span),  # STEP 8
            ).to_dict()
        )
    return out
```

Now the step-by-step of what `locate()` and `classify_skill()` do inside that loop:

```
STEP 0  raw_text               (len 180, NEVER mutated — the fixed ruler)
        "Skills: no experience with SQL, expert in Python, learning Excel. Education: ..."
```

```
STEP 1  needle = normalize("SQL")
        'sql'
        ↑ the search word, cleaned: lowercased, parentheses dropped
```

```
STEP 2a clean, index_map = normalize_mapped(raw_text)
        clean  (len 168):
        'skills no experience with sql expert in python learning excel education bsc ...'
        ↑ a CLEANED COPY of the ruler: lowercase, every run of spaces/punctuation
          squeezed to one space. The original is untouched; this is a derived twin.

STEP 2b index_map  (clean position → original rawText position)
        [0,1,2,3,4,5,6, 8,9,10,...]
        ↑ THE KEY TRICK. clean[7] came from raw[8] (the ':' + space collapsed, so
          positions shifted). This list is how we undo the cleaning later.
```

```
STEP 3  pos = exact_token_find(clean, 'sql')
        26
        clean[26:29] == 'sql'   ✓ whole word (not the 'sql' inside 'mysql')
        ↑ WHERE in the CLEANED text, not the original yet
```

```
STEP 4  map back:  start = index_map[26] = 27 ,  end = index_map[28]+1 = 30
        span = (27, 30)
        raw_text[27:30] == 'SQL'   ✓✓
        ↑ THE ROUND-TRIP. We found it in the clean copy, then used index_map to
          point at the EXACT original spot. clean-26 → raw-27. This is why
          highlights stay perfect even though we searched a cleaned copy.
```

```
STEP 5  clause, clause_start = clause_around(raw_text, 27, 30)
        clause       = 'Skills: no experience with SQL, expert in Python, learning Excel'
        clause_start = 0
        ↑ grow left/right from SQL to sentence boundaries (. ; ! ? newline | …).
          This sentence is what the rules will read. clause_start=0 = it begins at
          the very start of the ruler.
```

> **The method STEPS 1–5 came from** — `locate()` in `shared/locator.py`:
> ```python
> def locate(entity_text, raw_text):
>     needle = normalize(entity_text or "")                 # STEP 1
>     if not needle:
>         return None, None, None
>     clean, index_map = normalize_mapped(raw_text or "")   # STEP 2
>     pos = exact_token_find(clean, needle)                 # STEP 3
>     if pos != -1:
>         c_start, c_end = pos, pos + len(needle) - 1
>     else:
>         found = fuzzy_spaceless_find(clean, needle)       # backup for "S Q L"
>         if found is None:
>             return None, None, None
>         c_start, c_end = found
>     start = index_map[c_start]                            # STEP 4: map back
>     end = index_map[c_end] + 1
>     clause, clause_start = clause_around(raw_text, start, end)   # STEP 5
>     return clause, clause_start, (start, end)
> ```

```
STEP 6a _pieces(clause)   — cut the sentence at "walls" (, ; : | and/but/while/…)
        [ (0,'Skills'),
          (7,' no experience with SQL'),      ← SQL lives here
          (31,' expert in Python'),
          (49,' learning Excel') ]

STEP 6b _piece_around(clause,'SQL')  →  piece_start = 7
        ' no experience with SQL'
        ↑ THE PRECISION GUARD. We keep ONLY SQL's own piece. This is why the
          "expert" next door (Python's piece) can't leak onto SQL.
```

```
STEP 7  status, matched, pos = classify_skill(clause, 'SQL')
        ('no_experience', 'no experience', 8)
        ↑ run SKILL_RULES over the piece, worst-signal-first, first match wins.
          'no experience' matched. position 8 = where the cue sits in the clause.
```

```
STEP 8  evidence span = (clause_start + 8, clause_start + 8 + len('no experience'))
                      = (8, 21)
        raw_text[8:21] == 'no experience'   ✓✓✓
        ↑ map the cue's position back onto the ruler one more time. Now
          evidence.text and evidence.rawTextSpan describe the SAME thing.
```

**Final record appended** (the addition for SQL):
```json
{"entryIndex":0,"entity":"SQL","status":"no_experience",
 "confidence":"high","severity":"warning",
 "evidence":{"text":"no experience","rawTextSpan":[8,21]}}
```

Where did each field come from?
- `status` ← STEP 7 (the rules)
- `severity` ← `severity_of("skill","no_experience")` = **lookup** in the fixed
  `STATUS_SEVERITY` table → `"warning"` (never re-decided per resume)
- `confidence` ← `"high"` because STEP 4 found a real span (else `"low"`)
- `evidence` ← STEP 8 (text + round-tripped span)

---

## Same machinery, a different item: `"BSc Computer Science"`

Education/certification don't have their own brain — they share `status_engine.py`,
but the finder steps are identical:

```
locate("BSc Computer Science", raw_text)
   → clause       = 'Education: BSc Computer Science (withdrew 2016)'
   → clause_start = 66
   → span         = (77, 97)      raw_text[77:97] == 'BSc Computer Science' ✓
classify_status(clause, EDU_RULES)
   → 'incomplete'  (cue 'withdrew' matched)
severity_of("education","incomplete")  →  'warning'
```

Added record:
```json
{"entryIndex":0,"entity":"BSc Computer Science","status":"incomplete",
 "confidence":"high","severity":"warning",
 "evidence":{"text":"withdrew","rawTextSpan":[99,107]}}
```

---

## What if the rules DON'T match? (your question)

If no cue matches, or we can't even *find* the item in `rawText`, we **do not guess**.
We fall back to a quiet, no-signal status — and that fallback is **always `info`,
never `warning`**:

| Module | No cue matched | Couldn't locate the item |
|---|---|---|
| skill | → `"plain"` (info) | → `"plain"` (info), confidence `low` |
| education | → `"unknown"` (info) | → `"unknown"` (info), confidence `low` |
| certification | → `"unknown"` (info) | → `"unknown"` (info), confidence `low` |

So an incomplete rulebook costs us a **miss** (we stay silent on a real problem),
**never a false accusation** (we don't wrongly warn on a good candidate). "When unsure,
stay quiet." The item is still listed — we're a full mirror — it just carries no warning.

### A worked edge case — something our rules genuinely can't detect

Feed the engine this (real run):

```json
{ "data": {
    "skills": [ {"name":"Java"}, {"name":"Kubernetes"} ],
    "rawText": "Java is rusty these days, honestly a bit out of practice."
} }
```

A human reading this clearly sees a **weak** Java skill. But our lexicon has no entry
for "rusty" or "out of practice" — those phrasings simply aren't in `SKILL_RULES`. And
Kubernetes isn't in the text at all. Here's what actually comes back:

```json
[
  { "entryIndex":0, "entity":"Java", "status":"plain", "confidence":"high",
    "severity":"info", "evidence":{"text":"Java","rawTextSpan":[0,4]} },
  { "entryIndex":1, "entity":"Kubernetes", "status":"plain", "confidence":"low",
    "severity":"info", "evidence":{"text":"Kubernetes","rawTextSpan":null} }
]

summary: []     ← empty: nothing was raised as a warning
```

Two different "undetectable" situations, both handled the same safe way:

| Item | What happened | status | confidence | severity |
|---|---|---|---|---|
| **Java** | *found* in the text, but no cue word matched ("rusty" isn't in our rules) | `plain` | `high` (we located it) | `info` |
| **Kubernetes** | *not found* in the text at all — nothing to read | `plain` | `low` (couldn't locate) | `info` |

Notice the honesty built in:
- Java's evidence highlights the **word "Java" itself** (span `[0,4]`), not a cue — because there's no cue to point at. That's `build_evidence`'s "no match" branch.
- Kubernetes' evidence span is `null` and confidence is `low` — a quiet signal that *"we couldn't even find this, don't trust our silence here."*
- The `summary` is **empty**. We did **not** invent a warning for the rusty Java.

This is the deliberate trade-off, made visible: the "rusty Java" miss is a **false
negative** we accept, precisely so we never produce a **false positive**. These
`plain` / `low` items are exactly the pile a future LLM pass (or new lexicon entries
grown from real test data) would be aimed at — and because every miss is already
listed in the output, that pile is easy to find and measure.

---

## Before → After (what changed, in one view)

```
AFFINDA GAVE US                        WE HAND BACK (originalJSON unchanged +)
───────────────                        ──────────────────────────────────────
skills:                                enrichmentJSON.skills:
  {name:"SQL"}                 ──▶        SQL     → no_experience  warning  "no experience" @[8,21]
  {name:"Python"}              ──▶        Python  → strong         info     "expert"        @[32,38]
  {name:"Excel"}               ──▶        Excel   → learning       warning  "learning"      @[50,58]
education:                             enrichmentJSON.education:
  {qualification:"BSc …"}      ──▶        BSc …   → incomplete     warning  "withdrew"      @[99,107]
certifications:                        enrichmentJSON.certifications:
  {name:"AWS …"}               ──▶        AWS …   → expired        warning  "expired"       @[166,173]

summary:
  - Skill 'SQL' looks no experience.
  - Skill 'Excel' looks learning.
  - Degree 'BSc Computer Science' looks incomplete.
  - Certificate 'AWS Certified Solutions Architect' looks expired.
```

The left side is five bare names. The right side is five **judgements with proof**.
That gap — bare name → judged, sourced, severity-tagged record — is the enrichment.

---

## The three dials (keep these separate in your head)

Every added record carries three independent answers:

| Dial | Question it answers | Where it's decided |
|---|---|---|
| **status** | *What does the text say?* | the cue rules (first match wins) |
| **severity** | *How much should a recruiter care?* | fixed `STATUS_SEVERITY` lookup |
| **confidence** | *Did we actually find it in the text?* | `high` if located, else `low` |

`status` is read from the resume. `severity` is a frozen mapping from status. `confidence`
is just "did the finder succeed." Three different dials — don't let them blur together.
