# `delivery/docker/` — the container door

## In one line
Packages the HTTP API into a container so it runs the same way on any machine
("works on my laptop" → "works everywhere"). Two files: a `Dockerfile` (the recipe)
and a `docker-compose.yml` (the one-command runner).

## How you run it
```
docker compose -f resume_enricher/delivery/docker/docker-compose.yml up --build
```
Then the API is at **http://localhost:8000** (docs at `/docs`).

## `Dockerfile` — the recipe, step by step
| Line | Plain meaning |
|---|---|
| `FROM python:3.11-slim` | start from a small Linux box that already has Python 3.11 |
| `ENV PYTHONUNBUFFERED=1 …` | nicer logs, no stray `.pyc` files |
| `COPY requirements.txt` + `pip install` | install the three delivery deps **first**, so this slow step is cached until the deps change |
| `COPY resume_enricher ./resume_enricher` | copy the app package in |
| `CMD uvicorn …api:app --host 0.0.0.0 --port 8000` | start the web server, reachable from outside the container |

**Build context = the repo root** (the outer folder with `requirements.txt` and the
`resume_enricher/` package). The compose file sets that context for you.

## `docker-compose.yml` — the one-command runner
- Builds the image using the Dockerfile above (context three levels up).
- Maps container port `8000` → your machine's `8000`.
- Adds a **healthcheck** that calls `/health` every 30s (so Docker knows if it's alive).
- `restart: unless-stopped` — if it falls over, bring it back.

## Status in this environment
The Docker **CLI is installed** and `docker compose ... config` **validates** (the
YAML, the build-context path and the Dockerfile reference all resolve correctly).
The Docker **daemon isn't running here**, so the image hasn't been built/run on this
machine yet — that's the one step to do wherever a Docker daemon is available.

## Where it sits
The container just runs `delivery/api.py`, which runs `enrich()`. No new logic — it's
packaging, not brains.
