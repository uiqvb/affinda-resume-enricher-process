# `shared/validators.py` — the safety checks

This file has **no data shapes** (those live in [`models.md`](models.md)). It has
**three small methods** that act as **guards** around the real work.

Together they make our #1 promise — *never change Affinda's original data* —
impossible to break by accident.

---

## The three guards at a glance

| # | Method | Nickname | Runs | Its one job |
|---|--------|----------|------|-------------|
| ① | `validate_input`   | the **bouncer**     | before we start | reject broken input |
| ② | `deep_copy`        | the **photocopier** | before we start | make a private copy to work on |
| ③ | `ensure_untouched` | the **auditor**     | at the very end | prove the original never changed |

## How they wrap the real work

```
  resume in
     │
     ▼
  ① validate_input ....... bouncer:     is this even usable?
     │
     ▼
  ② deep_copy ............ photocopier: copy it, so we touch the copy — never the real thing
     │
     ▼
     ...enrich the COPY...  (the real work — Steps 2-6)
     │
     ▼
  ③ ensure_untouched ..... auditor:     is the original still exactly as it came in?
     │
     ▼
  result out
```

---

## ① `validate_input` — the bouncer

**In one line:** check the resume isn't broken before we start; stop with a clear
message if it is.

The checks, in order (it stops at the first one that fails):

```
① is the whole thing a labelled-box (a dictionary)?
② does it have a "data" section?
③ is that "data" section itself a labelled-box?
④ for each of skills / education / certifications that EXISTS: is it a list?

none failed  ->  let it through
```

**What's allowed (not errors):** a section can be **missing or empty** — that just
means "nothing to check there." A missing resume text is fine too (we just can't show
exact positions, so those enrichments get `low` confidence).

*(It checks the Affinda response, whose top-level key is `data`. `meta` and any other
top-level extras are ignored — they pass straight through.)*

### ✅ A valid resume — why each part passes
```jsonc
{
  "meta": { "ready": true },                  // extra top-level key -> ignored, totally fine
  "data": {                                   // ② it HAS a "data" section ...
    "name": { "raw": "Leo Farrow" },          //    ... and ③ "data" is a labelled-box ✓
    "skills":        [ {"name":"SQL"}, {"name":"Python"} ],      // ④ a list ✓
    "education":     [ {"accreditation":{"education":"BSc Computer Science"}} ], // ④ a list ✓
    "certifications":[ {"name":"AWS Certified"} ],              // ④ a list ✓
    "rawText": "Skills: no experience with SQL, expert in Python. BSc Computer Science."
  }
}
// ① the whole thing is a dictionary ✓   ->  passes ALL four  ->  bouncer lets it through
```
Note: `name` and `meta` aren't checked — we only guard the three lists we actually read.

### ❌ Invalid resumes — each blocked by a different check
```jsonc
// blocked by ①  (not a dictionary at all)
42
   -> ① a dictionary?  NO
   -> STOP: "the resume data should be a dictionary, but it isn't"

// blocked by ②  (no "data" section)
{ "meta": { "ready": true } }
   -> ① yes.  ② has "data"?  NO
   -> STOP: "the resume data is missing its 'data' section"

// blocked by ③  ("data" is there, but it's the wrong type)
{ "data": "Leo Farrow's resume text" }
   -> ① yes.  ② yes.  ③ is "data" a dictionary?  NO (it's text)
   -> STOP: "the 'data' section should be a dictionary, but it isn't"

// blocked by ④  (a section exists but isn't a list)
{ "data": { "skills": "SQL, Python" } }
   -> ① yes.  ② yes.  ③ yes.  ④ is "skills" a list?  NO (it's text)
   -> STOP: "'skills' should be a list, but it isn't"
```
The first failing check stops everything, so a resume with several problems reports
the earliest one.

---

## ② `deep_copy` — the photocopier

**In one line:** make a fully separate copy of the resume, so anything we do happens
on the copy and can never reach the original.

It must be a **deep** copy. Here's why that word matters:

```
SHALLOW copy (the dangerous kind):
   original ──┐
              ├──► the SAME inner skills list      ← both point at ONE list
   copy ──────┘
   edit the copy's skill  ->  the ORIGINAL changes too.   💥 promise broken

DEEP copy (what deep_copy does):
   original ──► its own skills list
   copy ──────► a SEPARATE skills list             ← fully independent
   edit the copy  ->  the original is untouched.          ✅
```

After `deep_copy` we have a private sandbox. We can scribble freely; Affinda's
original is safe.

---

## ③ `ensure_untouched` — the auditor

**In one line:** at the end, compare the original to what we're handing back; if they
differ at all, stop loudly.

```
is "what we return" identical to "what came in"?
   yes  ->  fine, promise kept
   no   ->  STOP: "we accidentally changed the original resume — this must never happen"
```

This is the safety net. Even if a bug upstream edited the original, this catches it
**before** we ship wrong data.

---

## A note on "STOP"

A method normally **returns** a value. "STOP" is the opposite: it **halts** the whole
job and raises an error the caller must handle. We only do it when carrying on would
be unsafe — bad input (①), or the original got changed (③).

*(In the Python code, STOP is `raise ValueError(...)` or `raise AssertionError(...)`.)*

---

## Where they sit in `enrich()`

```
METHOD Enrich(resume)
   validate_input(resume)                // ① bouncer:     not broken?
   original = deep_copy(resume)          // ② photocopier: safe copy to work on
   data     = original's "data"          //    read items from here (never write)

   ... find items, judge them, build Enrichment pieces ...   // the real work (Steps 2-6)

   ensure_untouched(resume, original)    // ③ auditor:     prove we changed nothing
   RETURN original + our enrichments     //    hand back an EnrichedJSON
```
The shapes used in the middle (**Enrichment**, **Evidence**, **EnrichedJSON**) live in
[`models.md`](models.md).
