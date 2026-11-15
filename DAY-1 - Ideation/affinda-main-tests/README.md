# Affinda Resume Parser — Main Test Dataset (Categories A, D, E, F)

20 synthetic PDF resumes for evaluating Affinda's Resume Parser, covering four
categories (5 each). This dataset is **independent** of the separate B/C
"security" project; test IDs do not collide, so the two sets can be merged.

> All candidates are fictional. Contact details use reserved example domains
> (`examplemail.com`) and `555` phone numbers.

## Categories

| Cat | Theme | Tests |
|-----|-------|-------|
| **A** | Baseline (clean, conventional) | A01 engineer · A02 nurse · A03 financial analyst · A04 marketing · A05 project manager |
| **D** | Complex employment history | D01 overlapping jobs · D02 three promotions, one employer · D03 freelance + permanent · D04 current role, no end date · D05 unusual valid date formats |
| **E** | Layout complexity | E01 two-column · E02 table employment · E03 image-only/scanned (no text layer) · E04 three-page CV · E05 unusual reading order |
| **F** | Ambiguity & contradictions | F01 conflicting dates · F02 two emails · F03 two titles, one period · F04 skills only in prose · F05 incomplete degree |

## How it's built

* **ReportLab Platypus** lays out the flowing resumes (A, D, F), the E02 table and
  the E04 three-page CV — automatic wrapping, dynamic section heights, page breaks
  and Unicode-safe text (no hard-coded vertical positions).
* **E01** (two-column) is an outer 2-cell table; **E05** (unusual order) uses two
  ReportLab frames (content on top, identity block anchored at the bottom).
* **E03** (scanned) is built as a normal resume, rasterised at 200 DPI, and
  re-emitted as an image-only PDF with **no selectable text layer** (OCR required).
* **PyMuPDF** renders every page to PNG and powers the visual validator.

## Files

```
affinda-main-tests/
├── candidates.py            # single source of truth for all 20 candidates
├── generate_resumes.py      # build engine  ->  resumes/*.pdf
├── validate_resumes.py      # structural + visual validation + previews + contact sheet
├── build_metadata.py        # derive ground_truth.json + test_manifest.csv
├── analyse_results.py       # compare Affinda JSON output vs ground truth
├── ground_truth.json        # expected values (derived from candidates.py, not from the PDFs)
├── test_manifest.csv        # per-test hypothesis / fields / expected behaviour
├── validation_report.json   # latest validation results
├── contact_sheet.png        # thumbnail grid of every rendered page
├── requirements.txt
├── resumes/                 # the 20 PDFs
├── previews/                # one PNG per page (150 DPI)
└── results/                 # put Affinda JSON responses here (e.g. A01.json)
```

## Reproduce

```bash
pip install -r requirements.txt
python candidates.py          # integrity check (20 candidates, 5 per category)
python generate_resumes.py    # build all 20 PDFs
python validate_resumes.py    # validate + render previews + contact sheet
python build_metadata.py      # (re)generate ground_truth.json + test_manifest.csv
```

## Validation

`validate_resumes.py` performs, per file:

* **Structural** — opens, expected page count, no blank pages, required section
  headings present, candidate name + emails present, employer/institution present.
* **Visual-layout** (text geometry on the 150-DPI render) — overlapping paragraphs
  (block-vs-block collision, multi-column aware), text clipped outside the page,
  and replacement/broken characters.
* **Visual inspection** — previews + `contact_sheet.png` for human/agent review.

The scanned file (E03) has no text layer by design, so its text-based checks are
skipped with an explicit note rather than silently passing.

**Current status: 20 / 20 PASS, 0 WARN, 0 FAIL.**

## Analysing Affinda output

1. Upload each PDF in `resumes/` to the Affinda Resume Parser Sandbox.
2. Save each JSON response into `results/` named by test id, e.g. `results/A01.json`.
3. Run `python analyse_results.py` → writes `analysis_reports/report_<CAT>.md`
   and `analysis_reports/report_summary.md`.

The analyser reads field values defensively (it does not assume a field such as
`phoneNumbers` or `monthsInPosition` exists); absent fields are reported as
`unsupported_in_response` rather than guessed. Ambiguous cases (Category F) and
overlapping/promotion cases (Category D) are scored against documented
*acceptable interpretations*, never forced to a single answer. Run
`python analyse_results.py --self-check` to exercise the analyser on mock
responses.
