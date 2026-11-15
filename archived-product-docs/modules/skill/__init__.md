# `modules/skill/__init__.py` — the skill module's front door

**In one line:** `run(skills, resumeText)` → one enrichment for **every** skill.

This is the only part of the skill module the rest of the tool talks to. Everything
else in the folder (`_classify.py`, `_rules.py`) is private machinery it calls.

---

## The three files in this folder

```
skill/
├── __init__.py   ◄ THIS file — the public door: run(skills, text)
├── _classify.py  ◄ the precision guard (decide a skill's status)      [_classify.md]
└── _rules.py     ◄ the cue words (which phrases mean which status)     [_rules.md]
```

The leading `_` means "private — don't call from outside." Only `run` is public.

---

## What `run` does

For **every** skill Affinda extracted (a complete mirror — nothing skipped):

```
for each skill:
    name  = the skill's name
    find it in the resume text               (locate, from locator.py)

    if not found:
        status = "plain",  no cue             (confidence will be "low")
    else:
        decide its status from its own piece  (classify_skill — the precision guard)

    build ONE Enrichment:
        entryIndex = position in Affinda's list
        entity     = the name
        status     = what we decided
        confidence = "high" if found, else "low"
        severity   = warning/info from the menu
        evidence   = proof, text + highlight lined up   (build_evidence)
```

Returns the list of enrichments. The orchestrator ([`../../app/enrich.md`](../../app/enrich.md))
drops that list straight into `enrichmentJSON.skills`.

---

## Why skills have their own module (not the shared engine)

Degrees and certificates use the shared [`status_engine`](../../shared/status_engine.md)
— one item per sentence, read the whole sentence. Skills can't: a single sentence often
lists several skills with different strengths, so skills need the **precision guard**
(read only this skill's piece). That extra care is why skills get their own
`_classify.py` instead of sharing the engine.
