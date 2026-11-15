# `modules/certification/_rules.py` — the certification cue words

**In one line:** the phrases that tell us whether a certificate is still valid. Pure
vocabulary; the engine that uses it is
[`../../shared/status_engine.md`](../../shared/status_engine.md).

---

## The six certification statuses

`CERT_RULES` is checked **top to bottom, first match wins**, worst/strongest signal
first.

| Order | Status | Severity | Means | Example cue words |
|-------|--------|----------|-------|-------------------|
| 1 | `expired` | ⚠️ warning | time ran out | "expired", "lapsed", "no longer valid", "out of date" |
| 2 | `revoked` | ⚠️ warning | taken away by issuer | "revoked", "rescinded", "struck off", "cancelled by" |
| 3 | `suspended` | ⚠️ warning | paused by issuer | "suspended", "under suspension", "temporarily withdrawn" |
| 4 | `pending` | ⚠️ warning | not earned yet / failed | "scheduled", "awaiting", "registered for", "did not pass", "failed" |
| 5 | `active` | info | valid now | "active", "current", "in good standing", "valid", "renewed" |
| — | `unknown` | info | couldn't tell | *(nothing matched)* |

> **Why these are warnings.** Affinda lists *"AWS Certified Solutions Architect"* whether
> it's current or expired three years ago. A recruiter assumes "listed = valid." The
> warnings surface the four cases where it isn't.

---

## A note on `pending`

`pending` deliberately groups two different "not a valid credential (yet)" cases:

- **not earned yet** — "scheduled", "awaiting result", "registered for the exam"
- **attempted and failed** — "did not pass", "unsuccessful", "failed"

Both mean the same thing to a recruiter: *there is no valid certificate here right
now.* If you later need to tell them apart, split `pending` into two statuses — and
remember to add the new one to the `certification` menu in
[`../../shared/models.md`](../../shared/models.md).

---

## Changing the vocabulary

Add a phrase to the right status's list; it takes effect immediately. Keep the order
(worst signals on top). New statuses must be added to the menu in
[`../../shared/models.md`](../../shared/models.md), or the tool stops loudly on first use.
