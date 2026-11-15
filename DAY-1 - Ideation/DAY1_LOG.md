# Day 1 — Ideation — Sprint 1 & Sprint 2 Log (Retrospective)

> **Phase:** Ideation.  **Main achievement / deliverable:** `ROUGH_SCOPE.md` — the validated
> product scope. Probed Affinda across 4 discovery rounds (183 synthetic resumes), pinned down
> the 3 target problems it drops, and logged the parser defects. Output = **the Rough Scope.**

*Point-in-time retrospective captured at the end of Day 1, to be translated later into a
proper Sprint 1 vs Sprint 2 breakdown. Preserved as written.*

---

## Timeline — including what you actually explored

Two sprints, each roughly **two hours of actual work**. Sprint 1 ran from midday until the
Round 1 "what breaks the parser" work was done (~2:00 PM); after a gap, Sprint 2 began at
~3:30 PM and — interrupted by a long early-evening break — finished just before 6:50 PM.

---

## Sprint 1 · ~12:05 PM – 2:00 PM (~2 hours)

*Company research → technology/idea selection → the first "what breaks the parser" round.*

### 1. ~12:05–12:45 PM · Company and product discovery
**Question:** What does Affinda actually build, and where could I contribute?

You explored the Resume Parser, Affinda Extract, Draftable, Affinda Control, Signal and
Sports. We discussed SEEK, enterprise recruitment workflows, how parsing becomes JSON, and
why a feature must matter to customers rather than simply look technically interesting.

**Outcome:** Resume Parser became the most accessible product for independent
experimentation.

### 2. ~12:45–1:30 PM · Technology and idea selection
**Question:** Can I build something novel in approximately four days?

You investigated GitHub, the free Sandbox, cloud versus self-hosted Docker, proprietary
models, version comparisons and API integration.

Ideas considered included candidate rediscovery, career-change analysis, parser regression
testing and generic validation dashboards.

**Outcome:** You moved away from ideas requiring SEEK's internal systems or duplicating
existing Affinda features.

### 3. ~1:30–2:00 PM · Round 1: 30 resumes
**Question:** What actually breaks the parser?

Claude Code generated six groups of five resumes: conventional, hidden text, AI-instruction
probes, complex employment histories, difficult layouts and contradictions.

You dealt with PDF rendering defects, overlapping text and the need for independent ground
truth.

**Outcome:** Affinda was excellent on ordinary extraction. Hidden text entered rawText in
5/5 cases without an observed visibility warning; the AI-directed instructions did not
succeed. **Finishing this round closed out Sprint 1.**

---

*Gap · ~2:00 – 3:30 PM — away from the desk before picking the work back up.*

---

## Sprint 2 · ~3:30 PM – 6:47 PM (~2 hours of work, around a long 5:00–6:07 PM break)

*Falsification rounds → product direction → consolidation. ~90 minutes before the break
(3:30–5:00) plus ~40 minutes after resuming (6:07–6:47).*

### 4. ~3:30–4:10 PM · Round 2: 45 resumes
**Question:** Are those initial anomalies genuine, repeatable defects?

You focused on the original D03 employer error, D04 open-ended date and F05 incomplete
degree.

**Results:** employer attribution 15/15 correct; employment dates 13/15 correct, with two
fabricated end dates; education status absent in 15/15, with six potentially misleading
qualification-date cases.

**Outcome:** You rejected employer attribution as a strong project basis and retained
education status plus the narrow employment-date issue.

### 5. ~4:10–4:50 PM · Round 3: 48 resumes
**Question:** Is there a more consequential weakness elsewhere in the API?

You tested negated skills, skill ownership, certification validity, work authorisation,
employment type and experience duration.

**Results** included five clear negated skills extracted, contractor→part-time,
volunteer→internship, and lost certification-status information. Work authorisation and
overlapping-duration handling were generally strong.

**Outcome:** Claim-Aware Skills became a serious third candidate, while certification status
could extend CareerGuard.

### 6. ~4:50–5:00 PM · Round 4 design begins (then paused)
**Question:** Which findings survive a deliberate attempt to disprove them?

You started planning 60 more resumes across the six Round 3 categories, with matched
controls, positive/negative examples, ambiguous cases and a results analyser — before
stepping away for a long break.

**Outcome:** The falsification plan was underway when work paused.

---

*Massive break · ~5:00 – 6:07 PM.*

---

### 7. 6:07–~6:47 PM · Round 4 design wrap-up, internship strategy & reset
**Question:** How do I finish the plan and preserve the research cleanly?

Resuming with about 40 minutes of Sprint 2 left, you completed the Round 4 design, discussed
Andrew Bird, Pirrie having seen your application, and why a measured working prototype would
be more persuasive than a long bug report. You then requested a new-chat handoff containing
all experiments, technology decisions, evidence caveats and product directions.

**Outcome:** Four-round evidence gathering locked in, a clean continuation prompt, and this
retrospective — closing out Sprint 2.

---

## The most important questions you asked

| Your question or challenge | What changed |
|---|---|
| Is the free parser actually what enterprises buy? | We distinguished the commercial parser family from enterprise-specific versions and workflows. |
| Is this an actual bug, or just unusual resume wording? | You required controlled follow-up tests instead of accepting isolated failures. |
| Does it matter if a human catches the mistake? | We assessed downstream automated screening, not just technical correctness. |
| Is a four-day prototype substantial enough? | We emphasised an API, evidence, UI and held-out validation rather than a few rules. |
| Does Affinda already have this capability? | We eliminated duplicate ideas and checked existing JSON fields. |
| Will Andrew appreciate this? | We shifted from collecting defects to demonstrating product judgement and engineering execution. |
| Can we test again to rule out partial findings? | Round 4 was designed as falsification, not confirmation bias. |

---

## Technologies and concepts you covered

**Engineering stack**
Claude Code, Codex, Python, ReportLab, PyMuPDF, PDF rendering, JSON analysis, Docker, REST APIs

**AI evaluation**
Synthetic datasets, ground truth, matched controls, prompt-injection probes, model regression, semantic extraction, false positives

**Document technology**
OCR, invisible PDF layers, text occlusion, bounding boxes, metadata, schema limitations, evidence provenance

**Product strategy**
ATS screening, SEEK, enterprise API customers, commercial impact, differentiation, MVP scope, internship positioning

---

## What survived, and what didn't

- **VisibleProof:** Hidden text reaches machine-readable extraction. Potential
  document-integrity improvement; no demonstrated successful attack.
- **CareerGuard:** Missing education and certification status, plus a reproducible narrow
  employment-date error.
- **Claim-Aware Skills:** Five clear negation cases produced extracted skills; requires
  Round 4 confirmation and careful interpretation of Affinda's skills schema.
- **Deprioritised:** Employer attribution, general work-authorisation extraction, overlap
  calculations and generic validation products.

---

## What you achieved — and the remaining gap

| Metric | Count |
|---|---|
| Actual resumes tested | 123 |
| Additional tests designed | 60 |
| Potential wrapper modules | 3 |

**The key transition:** At noon, you were exploring whether you could do something
impressive for Affinda. By the end of the afternoon, you had a repeatable evaluation
methodology, several findings you had actively challenged, and a modular product direction.

What you hadn't yet demonstrated was a completed production-quality correction, measured on
unseen resumes. That's the next substantive milestone.

**In one sentence:** You spent the day moving from company research → technical exploration
→ controlled API experimentation → eliminating weak ideas → defining three evidence-backed
product capabilities → planning how to turn them into something Andrew can actually
evaluate.

---

> **Note (added after capture):** this retrospective reflects the state at ~6 PM on Day 1,
> when Round 4 (60 resumes) was *designed but not yet run* — hence "123 actual / 60
> designed". Round 4 has since been executed and analysed (see `ROUND4_ANALYSIS.md`),
> bringing the total to 183 resumes tested; the negated-skills finding was confirmed 7/10 on
> the unseen set.
