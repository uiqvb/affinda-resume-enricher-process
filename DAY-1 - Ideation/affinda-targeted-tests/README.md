# Affinda Resume Parser — Targeted Failure Investigation (45 probes)

A controlled follow-up to the 30-resume study. 45 synthetic resumes (`T01–T45`)
systematically probe the three confirmed weaknesses, **one controlled variable at a
time**. This is a *diagnosis* study — **no product is built here** and **no Affinda
results are fabricated**. Generation + validation are complete; scoring runs once you
upload the PDFs and save the JSON.

> Fictional candidates; `examplemail.com` addresses and `555` phone numbers.

## Design

Within each phase everything is held fixed except the variable under test, so any
behaviour change is attributable to that variable. Paired layout controls (T13/T14,
T29/T30, T44/T45) isolate layout from content.

| Phase | IDs | Question | Controlled variable |
|---|---|---|---|
| **1 — Ongoing dates** | T01–T15 | Does the parser invent an end date for current roles expressed without "Present"? | date wording + layout |
| **2 — Employer attribution** | T16–T30 | Do adjacent/overlapping roles cause employer bleed, invented, or client-as-employer errors? | employer label / order / layout |
| **3 — Education status** | T31–T45 | Is in-progress/withdrawn/deferred status preserved, or does a completion date make it read as conferred? | status wording + layout |

Phase 1 fixes one engineer (Jordan Avery @ Thamesworks Cloud, start Oct 2021) and only
changes the end-date expression (T01 "Present" … T12 single date … T11 completed
control). Phase 2 fixes one designer and changes the employment arrangement/label
(T16 "Self-Employed" … T20 no employer … T25 multiple clients … T27 staffing agency).
Phase 3 fixes one analyst and changes the qualification status (T31 completed control …
T36 incomplete J.D. … T42 "not awarded" … T44/T45 mixed, flow vs table).

## Files

```
affinda-targeted-tests/
├── targeted_candidates.py        # 45 test definitions + ground-truth expectations
├── generate_targeted.py          # build engine -> resumes/*.pdf
├── validate_targeted.py          # structural + visual validation + previews + contact sheet
├── build_targeted_metadata.py    # -> ground_truth_targeted.json + test_manifest_targeted.csv
├── analyse_targeted_results.py   # scores real Affinda JSON (defensive, per-phase)
├── ground_truth_targeted.json
├── test_manifest_targeted.csv
├── validation_report.json
├── contact_sheet.png
├── requirements.txt
├── resumes/      (45 PDFs)   previews/ (45 PNGs)
├── results/      (empty — put Affinda JSON here)
└── findings/     (empty — analyser writes here once results exist)
```

## Reproduce

```bash
pip install -r requirements.txt
python targeted_candidates.py        # integrity check (45, 15/phase)
python generate_targeted.py          # build 45 PDFs
python validate_targeted.py          # validate + previews + contact sheet
python build_targeted_metadata.py    # ground truth + manifest
```

**Status: 45/45 generated, 45/45 PASS structural + visual validation**, contact sheet
rendered, and every controlled variable confirmed present in the rendered text.

## Each test's ground truth

`ground_truth_targeted.json` records, per test: identity, expected work/education, the
**exact source evidence**, the **controlled variable**, **expected parser behaviour**,
**acceptable alternate interpretations**, **confirmed-failure criteria**, and
**inconclusive criteria**. Scoring honours these — e.g. an open-ended date (T03) is
*acceptable* if the parser leaves the end unknown, and only a **fabricated** end date
is a failure; a missing education-status *field* is **inconclusive** (status_absent),
while a completion date emitted for a non-completed qualification is a **confirmed**
failure.

## Analysing Affinda output

1. Upload all 45 PDFs in `resumes/` to the Affinda Resume Parser Sandbox.
2. Save the JSON into `results/` — either one file per test (`T01.json` …) or a single
   combined list like `[{ "fileName": "T01.pdf", "response": {…} }, …]`.
3. `python analyse_targeted_results.py` → writes `findings/targeted_summary.md` and
   `findings/targeted_data.json` (verdicts, failure patterns by controlled variable,
   paired comparisons, evidence snippets).

The analyser reads the observed schema defensively (`data.person.name`, `data.contact`,
`data.workExperience[].dateRange`, `data.education`, `data.rawText`, `meta.document`),
scores only unambiguous expectations, and preserves ambiguous cases as *inconclusive*.
`python analyse_targeted_results.py --self-check` exercises the logic on mock responses.
**It never fabricates responses**; with `results/` empty it reports that and exits.
