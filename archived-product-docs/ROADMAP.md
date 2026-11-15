# Roadmap — where v2 goes

v1 is deliberately **rule-based and narrow**: three qualifier checks, exact-match cues,
fail-safe silence when unsure. That silence is not a dead end — it's a *labelled pile*
(`unknown` / `plain`, `confidence: low`) that tells v2 exactly where to aim.

Everything below is an **additive** change — new `modules/<name>/` folders and new
fallbacks — because the architecture (one-way deps, a feature registry) was built for it.

---

## Near-term (the obvious next modules)

### 1. Problem D — employment-date inconsistency module
Catch fabricated end-dates on open-ended roles (e.g. a "Present" role that also carries
a concrete end date). Deferred from v1 only because it needs its **own taxonomy + ~100
résumés** first, the same evidence discipline used for the first three gaps. Ships as
`modules/employment/` + one registry line.

### 2. Missing-entity flag (addresses Affinda "List B" gaps)
Scan `rawText` for skills/credentials that are present in the text but **absent from
Affinda's extracted lists** (Affinda sometimes drops them — e.g. "Bar admission" not
recognised as a cert). Surfaced as a *possibly-dropped* flag. Needs a guarded
skill/credential list to keep false alarms near zero.

### 3. Date caveat for education
When an incomplete/withdrawn/expected degree carries a graduation-looking end date,
warn that the year should not be read as a conferral date (another List-B interaction).

---

## Precision & recall upgrades

### 4. Fuzzy cue matching
Typo-tolerant matching (`regex` `{e<=1}`) on the **"killer" cues only** — the ones that
flip good→bad (`no_experience`, `incomplete`/`not_awarded`, `expired`/`revoked`/
`suspended`). Positive/soft cues stay exact to protect precision.

### 5. LLM fallback for the `unknown` pile
Route only the items v1 left `unknown`/`plain` (low confidence) to an LLM for a
second opinion — keeping the cheap, deterministic, explainable rule path as the default
and paying model cost **only** where rules abstain. This is why v1 fails safe instead of
guessing: it builds the exact queue the LLM should work.

### 6. Grow the lexicons from evidence
The remaining ~15–25% of v1 misses are phrasings not yet in the cue lists ("rusty",
"out of practice", "sadly never finished"). Each new blind-set evaluation adds the
real-world phrasings it surfaces — never invented ones.

---

## Product surface

### 7. Verbose / "report everything" mode
v1 already mirrors every item; a verbose switch would expand `summary` to include the
confirmed-good statuses too, for consumers who want the full picture rather than just
warnings. (Easy — the data is already there.)

### 8. Per-field confidence & scoring
As the blind-set corpus grows, graduate `confidence` from `high`/`low` to a calibrated
score, enabling consumer-side thresholds.

---

## Guardrails that stay fixed

Whatever v2 adds, these do **not** change:
- **Non-destructive** — Affinda's output is never edited.
- **Fail safe** — new capability may raise recall, but must never trade away precision
  on good candidates.
- **Explainable** — every verdict keeps exact textual evidence; an LLM verdict must cite
  its span too.
- **Additive architecture** — a new check is a new module + a registry line, nothing more.
