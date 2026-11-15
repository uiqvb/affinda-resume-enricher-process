# DAY-2 findings — two separate lists, don't mix them

The experiment produced **two independent outputs**. Keep them apart.

---

## 📘 LIST A — Enrichment opportunities → **[`LIST-A_RESULTS.md`](LIST-A_RESULTS.md)**

**What ResumeGuard is built on.** Three *qualifier* fields that are missing from
Affinda's documented v1 schema (confirmed absent, not just empty):

1. education → **completionStatus** (completed / withdrawn / in-progress / expected …)
2. certification → **validityStatus** (active / expired / revoked / suspended …)
3. skill → **claimStrength / denied** (expert … exposure … "no experience with")

These are *missing fields*. Affinda does not return them, and the docs say the key set
is fixed — so our layer adds value rather than duplicating the parser. **This is the
product.**

---

## 🐞 LIST B — Parser defects → **[`LIST-B_PARSER_DEFECTS.md`](LIST-B_PARSER_DEFECTS.md)**

**Bugs to report to Affinda.** Genuine extraction *mistakes* found along the way —
things the parser dropped, truncated, or got wrong. These are **not** what we build on;
they're a courtesy bug list for the Affinda team.

1. Mid-tier skills (Azure / Tableau / Spark) dropped inconsistently
2. "Bar admission" credential never extracted
3. "withdrawn <year>" emitted as a conferral end date
4. "Juris Doctor (JD)" mis-tagged as `master` (truncation looks common per docs)
5. ~~Certificate IV routing~~ — removed; it's **documented behaviour**, not a bug

---

## The difference in one line

- **List A = a field that isn't there** (we add it). → our product.
- **List B = a value the parser got wrong** (Affinda should fix it). → their bug list.

Removing an item from List B (as happened with the old Defect 5) has **no effect** on
List A.

## Supporting data in this folder
- `*_scored.json` / `ALL_scored.json` — per-row verdicts behind List A.
- `divergences.json`, `examples_before_after.json` — data for the visual artifacts.
