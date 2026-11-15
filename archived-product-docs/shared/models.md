# `shared/models.py` — the entity models (the shapes of our data)

This doc explains **one file**: `resume_enricher/resume_enricher/shared/models.py`.

Think of this file as the **entity models** — the *shapes* of our data. Like the
blank forms in an office: a form doesn't *do* anything, it just says "this kind of
record has these parts." Nothing here runs; it only describes shapes that the rest
of the tool fills in.

**Big idea:** we are a full **enricher**. For **every** item Affinda lists (every
skill, degree, certificate) we add one piece of metadata — its status — so our
output is a **complete mirror** of Affinda's list with extra context. Each piece
also carries a **severity** (`warning` = worth attention, `info` = fine / neutral)
so the customer can filter.

Written below as **pseudocode** (plain structure, no real programming language).

---

## See it first — where each shape lives in a real output

### The big idea (how the shapes nest)
```
EnrichedJSON ................ the WHOLE object we hand back  (Shape 3)
│
├── originalJSON ........... Affinda's output, kept 100% UNTOUCHED
│      └── fileName, parseMs, response → data → skills / education / … , rawText
│
└── enrichmentJSON ........ the part WE add ("a JSON of enrichments")
       ├── version, checksRun, summary
       ├── skills[] .........┐
       ├── education[] ......┼── ONE Enrichment per ORIGINAL item (complete mirror)  (Shape 2)
       └── certifications[] .┘
                     │
                     └── Enrichment ...... the metadata about one item
                            ├── entryIndex, entity, status, confidence, severity
                            └── evidence ──► Evidence = { text, rawTextSpan }  (Shape 1)
```

### The same thing as real JSON
Resume text: `"Skills: No experience with SQL. Expert in Python."`
```jsonc
{
  "originalJSON": {                       // ◄ Affinda's output, UNTOUCHED
    "response": { "data": {
      "skills": [ { "name": "SQL" }, { "name": "Python" } ],
      "rawText": "Skills: No experience with SQL. Expert in Python."
    } }
  },

  "enrichmentJSON": {                     // ◄ the part WE add
    "version": "1.0",
    "checksRun": ["skill", "education", "certification"],

    "skills": [
      {                                   // ◄ one Enrichment — a WARNING
        "entryIndex": 0, "entity": "SQL",
        "status": "no_experience", "confidence": "high", "severity": "warning",
        "evidence": { "text": "No experience with SQL", "rawTextSpan": [8, 31] }
      },
      {                                   // ◄ one Enrichment — just INFO (not dropped!)
        "entryIndex": 1, "entity": "Python",
        "status": "strong", "confidence": "high", "severity": "info",
        "evidence": { "text": "Expert in Python", "rawTextSpan": [33, 49] }
      }
    ],
    "education": [],
    "certifications": [],
    "summary": [ "Skill 'SQL' listed, but resume says 'No experience with SQL'." ]
  }
}
```
Note: **both** skills appear now — SQL as a `warning`, Python as `info`. We enrich
everything; the severity tells them apart. The customer shows `warning`s to
recruiters and keeps the `info` for their data platform.

---

## Enrichment "types" — same shape, grouped by which list it's in

A **skill enrichment**, an **education enrichment** and a **certification
enrichment** are all the same `Enrichment` shape — the "type" is simply **which
list it sits in**:
```
enrichmentJSON.skills[]          -> skill enrichments
enrichmentJSON.education[]       -> education enrichments
enrichmentJSON.certifications[]  -> certification enrichments
```
Each list holds **one enrichment per original item** of that type.

---

## Affinda vs us — 2 resumes each, side by side

### ① What AFFINDA returns (2 resumes) — flat, no small print
```jsonc
[
  { "fileName": "R1.pdf", "response": { "data": {
      "skills":    [ {"name":"SQL"}, {"name":"Excel"}, {"name":"Python"} ],
      "education": [ {"accreditation": {"education":"BSc Computer Science"}} ],
      "rawText":   "No experience with SQL. Learning Excel. Expert in Python. BSc Computer Science (withdrew 2016)."
  } } },

  { "fileName": "R2.pdf", "response": { "data": {
      "certifications": [ {"name":"AWS Certified"}, {"name":"PMP"} ],
      "rawText":        "AWS Certified (expired 2021). PMP (revoked)."
  } } }
]
```

### ② What WE return (same 2 resumes) — original untouched + a status for EVERY item
```jsonc
[
  // ── RESUME 1 ── every skill + the degree get an enrichment ──
  {
    "originalJSON": { /* ◄ exactly the R1 object above, UNCHANGED */ },
    "enrichmentJSON": {
      "version": "1.0", "checksRun": ["skill", "education", "certification"],
      "skills": [
        { "entryIndex": 0, "entity": "SQL",    "status": "no_experience", "confidence": "high", "severity": "warning",
          "evidence": { "text": "No experience with SQL", "rawTextSpan": [0, 22] } },
        { "entryIndex": 1, "entity": "Excel",  "status": "learning",      "confidence": "high", "severity": "warning",
          "evidence": { "text": "Learning Excel", "rawTextSpan": [24, 38] } },
        { "entryIndex": 2, "entity": "Python", "status": "strong",        "confidence": "high", "severity": "info",
          "evidence": { "text": "Expert in Python", "rawTextSpan": [40, 56] } }
      ],
      "education": [
        { "entryIndex": 0, "entity": "BSc Computer Science", "status": "incomplete", "confidence": "high", "severity": "warning",
          "evidence": { "text": "withdrew 2016", "rawTextSpan": [84, 97] } }
      ],
      "certifications": [],
      "summary": [
        "Skill 'SQL' listed, but resume says 'No experience with SQL'.",
        "Degree 'BSc Computer Science' appears incomplete (withdrew 2016)."
      ]
    }
  },

  // ── RESUME 2 ── both certificates get an enrichment ──
  {
    "originalJSON": { /* ◄ exactly the R2 object above, UNCHANGED */ },
    "enrichmentJSON": {
      "version": "1.0", "checksRun": ["skill", "education", "certification"],
      "skills": [], "education": [],
      "certifications": [
        { "entryIndex": 0, "entity": "AWS Certified", "status": "expired", "confidence": "high", "severity": "warning",
          "evidence": { "text": "expired 2021", "rawTextSpan": [15, 27] } },
        { "entryIndex": 1, "entity": "PMP",           "status": "revoked", "confidence": "high", "severity": "warning",
          "evidence": { "text": "revoked", "rawTextSpan": [35, 42] } }
      ],
      "summary": [
        "Certificate 'AWS Certified' appears expired (2021).",
        "Certificate 'PMP' appears revoked."
      ]
    }
  }
]
```

### The difference, in one line
```
Affinda gives:   a flat list of items, no context.
We give back:    THAT SAME list, untouched, inside originalJSON
                 +  enrichmentJSON  = ONE status per item (a full mirror),
                    each tagged warning or info so the customer can filter.
```
Resume 1 shows all **3 skills** (2 warnings + 1 info) plus the **degree**; resume 2
shows **both certificates** — a complete mirror, nothing dropped.

---

## Notation used here
```
SHAPE Name — "what it is"
   fieldName  = what kind of value it holds        (example)
```
A field can hold: some text, a number, a pair of numbers, "one choice from a list",
or even another whole SHAPE tucked inside.

---

## Shape 1: Evidence — "the proof behind an enrichment"
```
SHAPE Evidence
   text         = some words we found in the resume     ("no experience")
   rawTextSpan  = a pair (start, end)  OR  nothing       ((8, 21)  or  empty)
```

> **The alignment rule (important).** `text` and `rawTextSpan` must always describe
> the **same thing**. If the proof text is `"no experience"`, the span must point at
> `"no experience"` in the resume — not at the skill somewhere else in the sentence.
> This is a promise the whole tool keeps, enforced by the `build_evidence` helper below.

---

## Helper: build_evidence — "make a proof with its text and highlight lined up"
Not a shape — a tiny **method** that every feature calls so the alignment rule above
is kept in exactly one place. Two cases:
```
build_evidence(entityName, matched, matchPos, clauseStart, entitySpan):

   CASE 1 — we matched cue words (e.g. "no experience"):
        proof text      = the cue words
        proof highlight = where the cue sits in the whole resume
                        = clauseStart + matchPos ... + length of the cue
        //  clauseStart = where the sentence began in the resume
        //  matchPos    = where the cue began inside that sentence
        //  add them  -> where the cue begins in the whole resume

   CASE 2 — no cue words (status "plain"/"unknown"):
        proof text      = the item's own name   ("SQL")
        proof highlight = where the ITEM sits    (entitySpan)
```
Why it exists: before this helper, one feature set the proof text to the cue words
but the highlight to the *item's* location — so they pointed at different things.
`build_evidence` makes that mistake impossible.

---

## Shape 2: Enrichment — "one piece of enrichment"
The metadata we add about one single item. We make ONE for EVERY item.
```
SHAPE Enrichment
   entryIndex   = a whole number: which ORIGINAL item this is about (0 = the first)
   entity       = the item's name                          ("SQL")
   status       = ONE status from the fixed menu            (see "Allowed statuses" below)
   confidence   = "high"  OR  "low"       (how sure we are of the status)
   severity     = "warning"  OR  "info"   (worth attention, or just context)
   evidence     = an Evidence            <-- a whole proof shape, tucked inside
```

> ⚠️ `entryIndex` vs list position: because we now mirror every item, the lists
> usually line up with the original — but always trust `entryIndex` as the true
> pointer back to the original item, not the position.

---

## Shape 3: EnrichedJSON — "the final package we hand back"
```
SHAPE EnrichedJSON
   originalJSON    = Affinda's original response   (copied, and NEVER changed)
   enrichmentJSON  = a JSON of enrichments          (one per item + a summary)
```

---

## Allowed statuses + severity — the `STATUS_SEVERITY` table
One table does two jobs: it lists every allowed status (its keys = the official
menu), and it tags each as `warning` or `info`.
```
TABLE STATUS_SEVERITY

   skill:
      no_experience=warning  learning=warning  lapsed=warning  basic=warning
      intermediate=info      strong=info       plain=info

   education:
      in_progress=warning  expected=warning  incomplete=warning
      deferred=warning     not_awarded=warning
      completed=info       unknown=info

   certification:
      expired=warning  revoked=warning  suspended=warning  pending=warning
      active=info      unknown=info
```
Used two ways:
```
severity = STATUS_SEVERITY[type][status]     // stamp each enrichment warning/info

if status is NOT a key in STATUS_SEVERITY[type]   // a typo / bug
     -> fail loudly (don't silently ship a wrong status)
```
`plain` (skill: no strength words found) and `unknown` (edu/cert: couldn't tell) are
both real statuses here, tagged `info`. We still list them — that's the "complete
mirror": every item gets a line, even when the line just says "nothing notable."

---

## Summary
`models.py` defines three shapes — **Evidence** (the proof), **Enrichment** (one
piece of metadata about one item, with a severity and an Evidence inside), and
**EnrichedJSON** (originalJSON + enrichmentJSON) — plus the **STATUS_SEVERITY**
table (the allowed menu + warning/info tag) and the **build_evidence** helper that
keeps every proof's text and highlight lined up. The checks that *use* these shapes
live in the sibling file — see [`validators.md`](validators.md).
