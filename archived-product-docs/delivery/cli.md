# `delivery/cli.py` — the command-line door

## In one line
A thin terminal wrapper: it reads a JSON file, calls the one brain `enrich()`, and
prints the result. **No resume logic lives here.**

## How you run it
```
python -m resume_enricher.delivery.cli FILE [options]
```
(Single command, so you don't type a sub-command name — the file comes first.)

| Command | What you get |
|---|---|
| `... cli examples/sample_affinda.json` | the full `EnrichedJSON` (original + enrichment) |
| `... cli sample.json --enrichment-only` | just the `enrichmentJSON` (what we added) |
| `... cli sample.json --summary` | just the plain-English warning lines |
| `... cli sample.json --indent 0` | compact JSON (no pretty-printing) |

## What it does, step by step
1. **Read** the file the person pointed at (`json.loads`).
2. **Enrich** — hand the parsed JSON to `enrich()`. This is the only line that does real work.
3. **Print** whichever view was asked for.

## When things go wrong (handled, not crashing)
| Problem | What the user sees | Exit code |
|---|---|---|
| File isn't valid JSON | `That file isn't valid JSON: ...` (in red, on stderr) | `2` |
| JSON is the wrong shape (no `data`) | `Can't enrich this resume: ...` | `1` |
| File doesn't exist | typer's own "file does not exist" message | `2` |
| All good | the JSON / summary | `0` |

Exit codes matter so this can be used in scripts (`&&`, pipelines, CI).

## Where it sits
`delivery/cli.py` → imports `resume_enricher.enrich` → (app → modules → shared).
One-way dependency: the door imports the engine, never the reverse.
