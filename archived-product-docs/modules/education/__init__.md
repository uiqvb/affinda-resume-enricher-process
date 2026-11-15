# `modules/education/__init__.py` — the education module's front door

**In one line:** `run(degrees, resumeText)` → one enrichment for **every** degree,
by handing the education cue words to the shared status engine.

---

## A deliberately tiny file

The education module does almost nothing itself. All the real work — find the degree,
read its sentence, match cue words, build the enrichment — lives in the shared
[`status_engine`](../../shared/status_engine.md). This file just connects the two:

```
run(degrees, resumeText):
    return run_status(degrees, resumeText, EDU_RULES, kind = "education")
```

That's the whole file. It passes three things to the engine:

| It passes | Which is | From |
|-----------|----------|------|
| the degrees | the items to check | Affinda |
| `EDU_RULES` | the education vocabulary | [`_rules.md`](_rules.md) |
| `"education"` | which severity menu to use | [`../../shared/models.md`](../../shared/models.md) |

---

## Why so thin?

Because education and certification are the **same machine with different words**.
Keeping this file tiny means the shared engine holds the logic once, and each feature
only owns its **vocabulary**. To change how degrees are judged, you edit the words in
[`_rules.md`](_rules.md) — never this file.
