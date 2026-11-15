# Affinda Resume Parser — Round 3 Gap Discovery (48 probes)

48 synthetic resumes (`R301–R348`), 8 per category, probing **new** potential
shortcomings that the two existing project ideas do **not** cover (hidden-text
integrity = *VisibleProof*; education-status / employment-date verification =
*CareerGuard*). Generation + validation only — **no live API, no fabricated results**.

> Fictional candidates; `examplemail.com` / `555` contacts.

## Categories (8 each)

| IDs | Category | Question | Existing field to check first |
|---|---|---|---|
| R301–R308 | **Negated skills** | Are explicitly denied skills ("No experience with Java") wrongly extracted as skills? | `skills` |
| R309–R316 | **Work authorisation** | Is citizen / PR / sponsorship / expired status captured anywhere structured? | `workAuthorization` (verify it exists) |
| R317–R324 | **Skill ownership** | Are skills of *managed people* mis-attributed to the candidate? | `skills[].sources` |
| R325–R332 | **Experience duration** | Approx/part-time/overlap/gap/explicit-claim — double-count or fabricate? | `employmentMetrics`, `dateRange.durationMonths` |
| R333–R340 | **Certification status** | Expired/pending/failed/revoked — captured as status, or shown as held? | `certifications` |
| R341–R348 | **Employment type** | Contract/internship/volunteer/freelance distinguished from permanent? | `workExperience[].employmentType` |

Each category includes clear positive controls, negative controls, ambiguous cases
(scored *inconclusive*, never a definitive failure), and paired single-variable tests.

## Files

```
affinda-round3-tests/
├── round3_candidates.py       # 48 definitions + ground-truth expectations
├── generate_round3.py         # build engine -> resumes/*.pdf
├── validate_round3.py         # structural + visual validation + previews + contact sheet
├── build_round3_metadata.py   # -> ground_truth_round3.json + test_manifest_round3.csv
├── analyse_round3_results.py  # scores real Affinda JSON; checks existing fields first
├── ground_truth_round3.json   test_manifest_round3.csv   validation_report.json
├── contact_sheet.png   requirements.txt
├── resumes/ (48 PDFs)   previews/ (48 PNGs)
├── results/  (empty — Affinda JSON goes here)
└── findings/ (empty — analyser output)
```

## Reproduce

```bash
pip install -r requirements.txt
python round3_candidates.py      # integrity (48, 8/category)
python generate_round3.py        # build 48 PDFs
python validate_round3.py        # validate + previews + contact sheet
python build_round3_metadata.py  # ground truth + manifest
```

**Status: 48/48 generated, 48/48 PASS** structural + visual validation; every controlled
probe confirmed present in the rendered text; contact sheet rendered.

## Analysing Affinda output

1. Upload the 48 PDFs in `resumes/` to the Sandbox.
2. Save JSON into `results/` — per test (`R301.json …`) or one combined list.
3. `python analyse_round3_results.py` → `findings/round3_summary.md` + `round3_data.json`.

The analyser reads the observed schema defensively, and **before** reporting any gap it
checks whether an existing field (`skills`, `workAuthorization`, `skills[].sources`,
`employmentMetrics`, `certifications`, `workExperience[].employmentType`) already covers
the hypothesis. Verdicts: **confirmed / ambiguous / unsupported / correct**. Ambiguous
cases are never scored as definitive failures; absent fields are reported as *unsupported
in this response*, not asserted as internally missing.

`ROUND3_ANALYSIS.md` is authored only **after** real results are supplied.
