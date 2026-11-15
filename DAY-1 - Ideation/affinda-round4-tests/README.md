# Affinda Resume Parser — Round 4: Independent Confirmation & Falsification (60 probes)

60 **new** synthetic resumes (`R401–R460`), 10 per category, designed to independently
**confirm / narrow / disprove** Round 3's findings on genuinely new cases — not to make
Affinda fail. Generation + validation only; **no live API, no fabricated results**.

> Fictional candidates; `examplemail.com` / AU `5550` contacts. Reference date for all
> duration expectations: **2026-11-12**.

## Categories (10 each) & the Round-3 hypothesis each tests

| IDs | Category | Round-3 hypothesis under test | Existing field checked first |
|---|---|---|---|
| R401–R410 | **Negated skills** | denied skills extracted as possessed (strongest finding) | `skills` (+ provenance) |
| R411–R420 | **Skill ownership** | managed/others' skills attributed to candidate | `skills[].sources` |
| R421–R430 | **Certification validity** | expired/revoked/pending status not preserved | `certifications` |
| R431–R440 | **Employment classification** | contract/volunteer compressed/mis-typed | `workExperience[].employmentType` |
| R441–R450 | **Work authorisation** | validity/expiry/restrictions/conflicts preserved? | `workAuthorization` |
| R451–R460 | **Employment duration** | overlaps double-counted / fabricated end dates | `employmentMetrics`, `dateRange.durationMonths` |

Each category has explicit positive and negative controls, isolates one variable where
possible, and **flags multi-variable tests** (e.g. R409 ownership+affirmation) that cannot
attribute a single cause. Paired tests are linked in the ground truth (`paired_test_id`).

## Files

```
affinda-round4-tests/
├── round4_candidates.py       # 60 definitions + ground-truth expectations
├── generate_round4.py  validate_round4.py  build_round4_metadata.py  analyse_round4.py
├── ground_truth_round4.json   test_manifest_round4.csv   validation_report.json
├── contact_sheet.png   requirements.txt
├── resumes/ (60 PDFs)   previews/ (60 PNGs)
├── results/  (empty — Affinda JSON here)   findings/ (empty — analyser output)
```

## Reproduce

```bash
pip install -r requirements.txt
python round4_candidates.py      # integrity (60, 10/category)
python generate_round4.py        # build 60 PDFs
python validate_round4.py        # validate + previews + contact sheet
python build_round4_metadata.py  # ground truth + manifest
```

**Status: 60/60 generated, 60/60 PASS** structural + visual validation; every controlled
probe confirmed present in rendered text; contact sheet rendered and inspected.

## Analysing Affinda output

1. Upload the 60 PDFs in `resumes/` to the Sandbox.
2. Save JSON into `results/` — per test (`R401.json …`) or one combined list.
3. `python analyse_round4.py` → `findings/round4_summary.md` + `round4_data.json`.

The analyser reads the observed schema defensively; for each category it checks the existing
field **before** reporting a gap, separates literal mentions from semantic claims, and marks
each case **correct / confirmed / partial / ambiguous / unsupported / miss**. It distinguishes
a concept the **schema does not model** (unsupported) from a supported field that is
**populated incorrectly** (confirmed/partial), and flags within-response inconsistencies.

`ROUND4_ANALYSIS.md` (incl. the cross-round CONFIRMED/NARROWED/NOT-REPRODUCED comparison
vs Round 3) is authored only **after** real results are supplied.
