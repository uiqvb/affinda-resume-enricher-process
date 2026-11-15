# `tests/test_resume_enricher.py` — the safety net

**In one line:** 34 small checks that each read like a sentence — "given THIS resume
text, the tool should say THAT." If you change a rule and break a promise, the test
name tells you exactly which one.

---

## How to run them

From inside the `resume_enricher/` folder:

```
python -m unittest discover -s tests     # run everything (clean pass/fail summary)
python tests/test_resume_enricher.py         # same thing, direct
```

No extra libraries — this uses Python's built-in test tool. A green run prints `OK`.

---

## What's covered (8 groups)

| Group | Checks that… |
|-------|--------------|
| **TextCleaning** | cleaning lowercases + collapses but keeps word gaps; the index map points back exactly; whole-word find won't match inside a bigger word |
| **Finder** | the word is found with an exact highlight despite messy spacing; spaced-out "S Q L" is found; a missing word returns all-none; the sentence stops at a boundary |
| **SkillPrecisionGuard** | each skill reads only its own piece; Python is **not** dragged down by SQL's negative cue; a joining word ("but") also acts as a wall; a cue-less skill is "plain" |
| **EducationStatus** | withdrawn→incomplete; graduated→completed; future date→expected; "expected" with a past year is **not** expected |
| **CertificationStatus** | expired→expired; revoked→revoked; valid→active |
| **SeverityMenu** | a bad status is a warning; a fine status is info; an unknown status fails loudly |
| **EvidenceAlignment** | every highlight points at the exact text it claims; the fallback uses the entity when no cue matched |
| **SafetyGuards** | bad input is rejected; a sparse resume is accepted; the original is never changed; a sneaky change is caught |
| **FullPipeline** | output keeps the original + adds enrichment; one enrichment per item; the summary lists exactly the warnings; missing rawText drops confidence without crashing |

---

## The two promises these lock down

1. **Accuracy of the headline feature** — the precision-guard group is the one that
   proves "no experience with SQL, expert in Python" never calls Python `no_experience`.
2. **The core safety promise** — the SafetyGuards group proves we never mutate the
   caller's original resume, and that `ensure_untouched` would catch us if we did.

---

## Reading a failure

A red line looks like:

```
FAIL: test_python_is_not_dragged_down_by_sqls_negative_cue
```

The name *is* the specification. That test failing means the precision guard regressed
and Python is wrongly picking up SQL's "no experience" — look at
[`../modules/skill/_classify.md`](../modules/skill/_classify.md).
