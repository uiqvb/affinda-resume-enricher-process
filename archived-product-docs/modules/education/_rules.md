# `modules/education/_rules.py` — the education cue words

**In one line:** the phrases that tell us whether a degree was finished, abandoned, or
still underway. Pure vocabulary; the engine that uses it is
[`../../shared/status_engine.md`](../../shared/status_engine.md).

---

## The seven education statuses

`EDU_RULES` is checked **top to bottom, first match wins**, worst/strongest signal
first.

| Order | Status | Severity | Means | Example cue words |
|-------|--------|----------|-------|-------------------|
| 1 | `in_progress` | ⚠️ warning | still studying | "currently enrolled", "pursuing", "candidate for", "ABD" |
| 2 | `expected` | ⚠️ warning | not finished, future date | "expected", "anticipated", "graduating", "due" |
| 3 | `incomplete` | ⚠️ warning | started, not finished | "withdrew", "discontinued", "dropped out", "did not complete" |
| 4 | `deferred` | ⚠️ warning | paused | "deferred", "on leave", "study break", "intermission" |
| 5 | `not_awarded` | ⚠️ warning | finished study, no degree | "not awarded", "requirements not met", "exams not passed" |
| 6 | `completed` | info | finished, degree earned | "graduated", "conferred", "awarded", "completed", "earned" |
| — | `unknown` | info | couldn't tell | *(nothing matched)* |

> **Why these are warnings.** Affinda lists *"BSc Computer Science"* the same whether it
> was earned or abandoned. A recruiter reading "BSc Computer Science" assumes a finished
> degree. The warnings surface the five cases where that assumption is wrong.

---

## The one special rule: `expected`

`expected` is the only status with an extra condition, enforced by the engine (not
here): the sentence must also mention a **future year**.

```
"BSc Physics, expected 2027"  ->  expected    ✓  (future year present)
"BSc Physics, expected 1999"  ->  skip it         (year is in the past)
```

This stops an old resume that says "expected 2015" from being flagged as an upcoming
degree. See [`../../shared/status_engine.md`](../../shared/status_engine.md).

---

## Changing the vocabulary

Add a phrase to the right status's list; it takes effect immediately. Keep the order
(worst signals on top). A brand-new status must also be added to the `education` menu in
[`../../shared/models.md`](../../shared/models.md), or the tool stops loudly on first use.
