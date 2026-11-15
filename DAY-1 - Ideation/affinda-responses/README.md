# Affinda Sandbox Responses — by round

Raw JSON responses returned by the Affinda Resume Parser Sandbox, organised by test round.
Each round's responses are also copied into that round's project `results/` folder (where
the analyser scripts read them).

| Round | File here | Docs | Tests | Project | Report |
|---|---|---|---|---|---|
| 1 | `round-1/round1-responses-30.json` | 30 | A/B/C/D/E/F (main + security) | `affinda-main-tests/`, `affinda-security-tests/` | `AFFINDA_ANALYSIS.md` |
| 2 | `round-2/round2-responses-45.json` | 45 | T01–T45 (targeted) | `affinda-targeted-tests/` | `TARGETED_ANALYSIS.md` |
| 3 | `round-3/round3-responses-48.json` | 48 | R301–R348 (gap discovery) | `affinda-round3-tests/` | `ROUND3_ANALYSIS.md` |
| 4 | `round-4/round4-responses-60.json` | 60 | R401–R460 (confirmation / falsification) | `affinda-round4-tests/` | `ROUND4_ANALYSIS.md` |

`_raw-exports/` holds the original Sandbox export files as downloaded:
- `affinda-resumes (1).json` — combined export of rounds 1 + 2 (75 docs).
- `affinda-resumes (2).json` — round 3 export (48 docs).
- `affinda-resumes (3).json` — round 4 export (60 docs).

The round-1 and round-2 per-round files were split out of the combined `(1)` export.
If you re-download a standalone round-1 file, drop it into `round-1/`.
