# `app/enrich.py` — the orchestrator (the whole pipeline)

**In one line:** `enrich(affinda)` runs the whole tool end to end and hands back
`{ originalJSON, enrichmentJSON }`. This is the one method everything else exists to
serve.

---

## The pipeline, in six steps

```
enrich(affinda):

   1. VALIDATE    — is the input usable?           (validators.validate_input)
                    broken shape -> stop with a clear error

   2. COPY        — make a safe deep copy to read from   (validators.deep_copy)
                    we read from the copy, never the caller's object

   3. RUN FEATURES — for each registered feature (skill, education, certification):
                     call its run(items, resumeText) -> a list of enrichments
                     drop that list into enrichmentJSON under its key

   4. SUMMARISE   — walk every enrichment; for each WARNING, write one
                    plain-English line a recruiter can read

   5. PROVE       — check the original is byte-for-byte unchanged
                    (validators.ensure_untouched) — our core promise

   6. RETURN      — { originalJSON: the untouched copy,
                      enrichmentJSON: everything we added }
```

---

## Step 3 up close — how features get run

The orchestrator doesn't name the features directly. It reads them from the
**registry** ([`registry.md`](registry.md)) — one list, the single place features are
registered:

```
for each feature in the registry:
    run_fn, inputKey, outputKey = the registry entry
    enrichment[outputKey] = run_fn( data[inputKey] or [] , resumeText )
```

So adding a fourth feature later means adding **one line to the registry** — this
orchestrator doesn't change at all. (You can also pass `enrich(affinda, modules=[...])`
to run just some features, e.g. only skills.)

---

## Step 4 up close — the summary

```
_build_summary(enrichment):
    lines = []
    for each list (skills, education, certifications):
        for each enrichment in it:
            if its severity is "warning":
                write one line:  "<Label> '<entity>' looks <status>."
    return lines
```

Example output:

```
Skill 'SQL' looks no experience.
Skill 'Excel' looks learning.
Degree 'BSc Computer Science' looks incomplete.
Certificate 'AWS Certified Solutions Architect' looks expired.
```

Only **warnings** appear here — the `info` items are still in the full lists for a
complete mirror, just not surfaced in the human summary. (The label map turns the
internal keys into friendly words: `skills`→"Skill", `education`→"Degree",
`certifications`→"Certificate".)

---

## The shape it returns

```
{
  "originalJSON":   Affinda's response, copied and UNTOUCHED,
  "enrichmentJSON": {
      "version", "checksRun",          // which features ran
      "skills":[], "education":[], "certifications":[],   // one enrichment per item
      "summary":[]                     // one line per warning
  }
}
```

Full shape reference: [`../shared/models.md`](../shared/models.md).

---

## Why validation wraps the whole thing

Steps 1 and 5 are the guardrails: **check before** (don't choke on broken input) and
**prove after** (never hand back a changed original). Everything useful happens between
them, on a copy. See [`../shared/validators.md`](../shared/validators.md).
