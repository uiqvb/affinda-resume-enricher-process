# `shared/status_engine.py` — the shared status engine

**In one line:** the single engine that reads a sentence and decides a **degree's**
or a **certificate's** status. Education and certification both use it; skills do not.

---

## Why one engine for two features

Education and certification ask the **same question**: *"looking at the sentence
around this item, what's its status?"* A degree might be `completed`, `incomplete`,
`expected`… A certificate might be `active`, `expired`, `revoked`… The *words* differ,
but the **machinery** is identical: find the item, read its sentence, match cue words,
pick the first that fits.

So we write that machinery **once** here, and each feature just hands in its own list
of cue words:

```
education module ──┐
                   ├──►  run_status(items, resumeText, THEIR_rules, kind)
certification ─────┘
```

> Skills are the exception — they need the stricter **precision guard** (several
> skills per sentence), so they have their own classifier. See
> [`../modules/skill/_classify.md`](../modules/skill/_classify.md).

---

## The three methods

| Method | Plain job |
|--------|-----------|
| `run_status` | the public door: make **one** enrichment for **every** item |
| `classify_status` | read one sentence, return `(status, matched words, position)` |
| `_has_future_year` | helper: does the sentence mention a year later than now? |

---

## `run_status(items, resumeText, rules, kind)` — the loop

For **every** item in the list (a complete mirror — we never skip):

```
for each item:
    name   = the item's qualification or name
    find it in the resume text          (uses locate, from locator.py)

    if not found:
        status = "unknown",  no matched words        (and confidence will be "low")
    else:
        read the sentence and classify it            (classify_status below)

    build ONE Enrichment:
        entryIndex = its position in the original list
        entity     = the name
        status     = what we decided
        confidence = "high" if we found it, else "low"
        severity   = warning/info, looked up from the status menu
        evidence   = the proof, with text + highlight lined up  (build_evidence)
```

The result is a list of enrichments, one per item — handed back to the feature module,
which hands it to the orchestrator.

---

## `classify_status(sentence, item, rules, thisYear)` — the decision

```
look at every rule in ORDER (first match wins):
    for each cue pattern in the rule:
        if the pattern appears in the sentence:

            SPECIAL CASE — "expected":
                only counts if the sentence ALSO names a future year.
                (otherwise skip it — "expected" with a past year is a mistake)

            return (this status, the exact words matched, where they start)

nothing matched  ->  return ("unknown", nothing, nowhere)
```

**Order matters.** The rule lists are written worst/strongest-signal first, so a clear
"withdrew" beats a softer "completed" if both somehow appear.

---

## The "expected needs a future year" rule — why

The word *"expected"* only means an unfinished, upcoming qualification when there's a
future date attached:

```
"BSc Physics, expected 2027"   ->  expected   ✓   (2027 is in the future)
"BSc Physics, expected 1999"   ->  NOT expected    (1999 is long past — ignore the word)
```

`_has_future_year` scans the sentence for any 4-digit year (`19xx`/`20xx`) and checks
whether it's later than the current year.

---

## What feeds in — the cue rules

This engine is deliberately empty of vocabulary. The actual cue words live with each
feature:

- degrees → [`../modules/education/_rules.md`](../modules/education/_rules.md)
- certificates → [`../modules/certification/_rules.md`](../modules/certification/_rules.md)

That's the whole trick: **one engine, two vocabularies.**

---

## Honest limitations (for later)

- It reads the **whole sentence** for the item (no precision-guard splitting). That's
  fine when there's one degree/certificate per sentence (the normal case). Two in one
  sentence could cross wires — noted for a future upgrade.
- Cue matching is exact (no typo tolerance yet) — the same deferred "fuzzy" upgrade as
  the skill rules.
