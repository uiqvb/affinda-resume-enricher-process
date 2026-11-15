# Resume Enricher — Dependency Map

> **How to read this:** `A → B` means **"A uses B"** (imports it / calls it). The whole point
> of the design is that arrows only ever point **down the tiers**:
> `delivery → app → modules → shared`. Nothing in `shared` ever reaches back up, and the three
> feature modules never call each other. This file is the proof of that, file by file.

---

## 0. The vertical flow — one function to the next

Follow it top to bottom. Each `─` note says, roughly, what that step does. Indented calls are
the helpers a step reaches into before handing back.

```
main()                               ─ load the résumé JSON, then call ▼
│
enrich(affinda)                      ─ the manager; runs the whole pipeline
│
├─ validate_input()                  ─ is the input broken? if so, stop
├─ deep_copy()                       ─ make a safe photocopy to work on
├─ read data + rawText               ─ pull the lists + text out of the copy
│
├─ FOR EACH check in the REGISTRY    ─ skill → education → certification
│   │
│   ├─ skill.run(skills, rawText)    ─ loop every skill; for each one:
│   │    ├─ locate(name, text)              ─ find the word + its sentence
│   │    │    ├─ normalize()                     ─ clean the search word
│   │    │    ├─ normalize_mapped()              ─ clean the text, keep an index map
│   │    │    ├─ exact_token_find()              ─ find it as a whole word
│   │    │    └─ clause_around()                 ─ widen out to the sentence
│   │    ├─ classify_skill(clause, name)    ─ decide the strength
│   │    │    ├─ _piece_around()                 ─ cut at walls, keep THIS skill's piece
│   │    │    └─ match SKILL_RULES               ─ first matching cue wins
│   │    ├─ severity_of()                   ─ warning or info?
│   │    ├─ build_evidence()                ─ the proof: matched words + their span
│   │    └─ Enrichment(...).to_dict()       ─ package one finished record
│   │
│   └─ education.run / certification.run    ─ both just call the shared engine:
│        └─ run_status(entries, text, RULES)
│             ├─ locate()                        ─ the SAME finder as above
│             ├─ classify_status()               ─ first matching cue wins
│             │    └─ _has_future_year()         ─ 'expected' only if a future year
│             ├─ severity_of()
│             ├─ build_evidence()
│             └─ Enrichment(...).to_dict()
│
├─ _build_summary()                  ─ one plain-English line per WARNING
├─ ensure_untouched()                ─ prove the original was never changed
│
▼
return { originalJSON,               ─ hand back: Affinda untouched
         enrichmentJSON }                        + our labels
```

**The shape to notice:** every feature funnels into the same three shared helpers at the
bottom — `locate()` (find it), the rules (label it), then `severity_of` + `build_evidence` +
`Enrichment` (package it). Skills take a slightly longer path (the precision guard); education
and certification share one engine. That's the whole program.

---

## 1. The call tree (follow one run, top to bottom)

```
main.py                                    [delivery — the "press play" button]
 └─ enrich()                               [app/enrich.py]      ← the manager
      ├─ validate_input()                  [shared/validators.py]
      ├─ deep_copy()                       [shared/validators.py]
      ├─ ensure_untouched()                [shared/validators.py]
      ├─ _build_summary()                  [app/enrich.py — its own helper]
      └─ REGISTRY  (loops it)              [app/registry.py]
           ├─ skill.run()                  [modules/skill/__init__.py]
           │    ├─ classify_skill()        [modules/skill/_classify.py]
           │    │     └─ SKILL_RULES       [modules/skill/_rules.py]
           │    ├─ locate()                [shared/locator.py]
           │    └─ Enrichment,             [shared/models.py]
           │       build_evidence,
           │       severity_of
           ├─ education.run()              [modules/education/__init__.py]
           │    ├─ EDU_RULES               [modules/education/_rules.py]
           │    └─ run_status()            [shared/status_engine.py]
           └─ certification.run()          [modules/certification/__init__.py]
                ├─ CERT_RULES              [modules/certification/_rules.py]
                └─ run_status()            [shared/status_engine.py]
```

Notice `education` and `certification` are almost empty — they just hand their own rules to the
**shared** `run_status()`. The skill module is the only one with its own classifier (because of
the precision guard).

---

## 2. The shared foundation (what the bottom tier depends on)

```
status_engine.run_status()                 [shared/status_engine.py]
 ├─ classify_status()        (same file)
 │    └─ _has_future_year()   (same file)
 ├─ locate()                               [shared/locator.py]
 └─ Enrichment, build_evidence, severity_of [shared/models.py]

locator.locate()                           [shared/locator.py]
 ├─ normalize()                            [shared/matching.py]
 ├─ normalize_mapped()                     [shared/matching.py]
 ├─ exact_token_find()                     [shared/matching.py]
 ├─ fuzzy_spaceless_find()                 [shared/matching.py]
 └─ clause_around()           (same file)

matching.py    → imports only `re`           (stdlib)   ← LEAF (depends on nothing of ours)
models.py      → imports only `dataclasses`  (stdlib)   ← LEAF
validators.py  → imports only `copy`         (stdlib)   ← LEAF
*/_rules.py    → import nothing (plain lists)            ← LEAF
```

The four **LEAF** files are the bedrock: they depend on *nothing* inside the project, so they
can never be broken by a change elsewhere. Everything else is built on top of them.

---

## 3. Focus: how `locate()` is used (the question that started this)

`locate()` (in `shared/locator.py`) is the shared **finder** — "where is this word in the
résumé text, and what sentence surrounds it?" It sits in the middle: it *has callers above it*
and *callees below it*.

**Who calls `locate()` (above it):**
| Caller | File | Serves |
|---|---|---|
| `skill.run()` | `modules/skill/__init__.py` | skills (directly) |
| `run_status()` | `shared/status_engine.py` | education **and** certification (through the engine) |

So although `locate()` has only **two** direct callers, it effectively serves **all three**
features — education and certification reach it indirectly via the status engine.

**What `locate()` uses (below it):**
```
locate()  →  matching.normalize
          →  matching.normalize_mapped
          →  matching.exact_token_find
          →  matching.fuzzy_spaceless_find
          →  clause_around()   (its own helper, same file)
```
`locate` is the *brain* (decides what to find); `matching.py` is the *hands* (the raw text
mechanics). That split is deliberate — see the design notes below.

---

## 4. `models.py` — the "nouns" everyone passes around

`models.py` is imported by **both** the skill module and the status engine. It defines the
**shapes** that travel through the whole pipeline:

- `Evidence`, `Enrichment` — the data shapes (the records we build)
- `build_evidence()` — the builder that makes an `Evidence`
- `STATUS_SEVERITY` + `severity_of()` — the status→severity lookup
- `EnrichedJSON` — **defined but unused** (dead code — see the audit log)

It depends on nothing internal, so it's pure vocabulary. Every file "speaks models."

---

## 5. The one-way rule (why this counts as a "modular monolith")

```
delivery   main.py
   │  (uses)
   ▼
app        enrich.py ──uses──► registry.py
   │  (uses)
   ▼
modules    skill/ · education/ · certification/      (never import each other)
   │  (uses)
   ▼
shared     models · validators · matching · locator · status_engine
           (imports only the Python standard library — never a module/app file)
```

**Verified:** no file in `shared/` imports anything from `modules/` or `app/`; no module
imports another module. That one-way flow is what lets you (a) change a feature without
touching the shared core, and (b) add a new feature as a new `modules/<name>/` folder plus one
line in `registry.py`, touching nothing else.

---

*This map is an audit aid — plain facts about who-uses-whom. Rewrite it in your own words
whenever you like; it just needs to stay true to the imports.*
