# `delivery/api.py` — the HTTP door

## In one line
Turns Resume Enricher into a tiny web service so a data platform can POST an Affinda
response and get the `EnrichedJSON` back. **No resume logic lives here** — it just
hands the body to `enrich()`.

## How you run it
```
uvicorn resume_enricher.delivery.api:app --reload
```
Then open **http://127.0.0.1:8000/docs** — FastAPI auto-builds a test page where you
can paste a resume and click "Execute".

## The endpoints
| Method + path | Body | Returns |
|---|---|---|
| `GET /health` | — | `{"status":"ok"}` — a cheap "is it alive?" check (used by Docker) |
| `POST /enrich` | a full Affinda response (JSON object with a `data` section) | `{ originalJSON, enrichmentJSON }` |

## What happens on a POST
1. FastAPI receives the JSON body as a plain dictionary.
2. It calls `enrich(affinda)` — the same brain the CLI uses.
3. Success → returns the `EnrichedJSON` as JSON.
4. Bad shape (e.g. no `data`) → `enrich()` raises `ValueError`, which we turn into a
   tidy **HTTP 422** with the plain-English reason (instead of a 500 crash).

## Verified behaviour (from the build test)
- `GET /health` → `{"status":"ok"}`
- `POST /enrich` with the sample → `originalJSON` came back **untouched**, and the
  `enrichmentJSON.summary` listed all four warnings.
- `POST /enrich` with `{"nope": true}` → **HTTP 422** (not a crash).

## Why `dict` and not a strict schema?
Affinda's real response has hundreds of fields. We deliberately accept any JSON
object and let `enrich()`'s own validator (the bouncer) decide if it's usable —
simpler, and it means we never reject a valid Affinda field we hadn't listed.

## Where it sits
`delivery/api.py` → imports `resume_enricher.enrich`. Same one-way dependency as the CLI.
