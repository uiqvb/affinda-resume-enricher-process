# DAY-2 Experiments — 300 resumes for the three ResumeGuard enrichments

Built from the `taxonomy/` CSVs (100 rows each). One taxonomy row → one one-page
synthetic resume that embeds that row's `exact_source_line` **verbatim**, in its
assigned location/layout, surrounded by ordinary resume content so Affinda parses
normally. Nothing is scored here and Affinda is **not** called — this only produces
the PDFs + ground truth + manifest so the returned parser JSON can be scored later.

## The three problems (100 each)

| Folder | Issue | Probe lands in | Layout axis |
|---|---|---|---|
| `education/` | education completion status (Problem B) | EDUCATION entry | flow / bulleted / table / two_column (from CSV) |
| `certification/` | certification validity (Problem C) | CERTIFICATIONS entry | flow / bulleted / table / two_column (from CSV) |
| `skill/` | skill claim strength / negation (Problem A) | `location`: skills_list / summary_prose / experience_bullet / proficiency_table / parenthetical | doc layout cycled for coverage |

Each folder has: `resumes/<ID>.pdf` (100), `ground_truth_<issue>.json` (every CSV
field + identity + filename, keyed by test_id), `manifest_<issue>.csv`.

- IDs: `E001–E100`, `C001–C100`, `S001–S100`.
- Controls (`is_control=True`) must pass — if they fail, our future detector is broken, not Affinda.
- Skill distractors (`is_distractor=True`) are precision traps (affirmed skill next to a denied one).
- `_build_report.json` records pages + probe-text verification (300/300 verified).

## Reproduce
```
python build_experiments.py            # all 300
python build_experiments.py E001 S044  # named subset
```

## Handoff / next step
1. Parse all 300 PDFs through the Affinda Sandbox (same as prior rounds).
2. Export the responses as JSON and hand them back.
3. We score each response against `ground_truth_*.json` (the `failure_if` per row is
   machine-readable), roll up detection rate / false-positive rate / rate-by-realism,
   and see exactly which phrasings and layouts each gap survives on.
