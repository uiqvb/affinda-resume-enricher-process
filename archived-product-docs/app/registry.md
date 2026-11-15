# `app/registry.py` — the one list of features

**In one line:** the single place every feature is registered. The orchestrator reads
this list to know what to run.

---

## Why a registry exists

Without it, the orchestrator would have to name skills, education and certification
directly — and you'd edit the orchestrator every time you added a feature. Instead, the
orchestrator reads this one list and runs whatever it finds. Features are **plugged in**
here, not wired into the pipeline.

```
REGISTRY = {
   "skill":         ( skill.run,         "skills",         "skills"        ),
   "education":     ( education.run,      "education",      "education"     ),
   "certification": ( certification.run, "certifications", "certifications"),
}
```

---

## What each line means

Each entry maps a feature name to **three** things:

| Part | Meaning | Example |
|------|---------|---------|
| run function | the feature's public door to call | `skill.run` |
| input key | where to read its items in Affinda's `data` | `"skills"` |
| output key | where to put its enrichments in our output | `"skills"` |

So the orchestrator can do, for every line:

```
items  = affinda.data[ inputKey ]      // read Affinda's items
result = runFunction(items, rawText)   // enrich them
enrichmentJSON[ outputKey ] = result   // store under our key
```

The input and output keys happen to match today, but keeping them separate means a
feature could read one Affinda field and write under a different name if ever needed.

---

## Adding a feature later — the whole checklist

1. Build the module folder (a `run(items, text)` door, like the others).
2. Add **one line** here.
3. Add its statuses to the menu in [`../shared/models.md`](../shared/models.md).

That's it — the orchestrator ([`enrich.md`](enrich.md)) picks it up automatically.
