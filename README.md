# MovieFone Manhattan showtimes API

Unofficial recreation of the lookup brain behind classic MovieFone (777-FILM). **Not affiliated with MovieFone, Fandango, AMC, Regal, or Alamo Drafthouse.**

This repo is a small FastAPI service the Grok voice agent will call later. Callers say a **ZIP**, then a **movie name**. Coverage is **Manhattan only**.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# optional: replace MF_API_KEY, or mint one:
python -m app.keys create --name local
uvicorn app.main:app --reload --port 8000
```

On boot the app loads `data/theaters.json`, `data/zips.json`, and the latest snapshot under `data/snapshots/` into SQLite. The seed snapshot is enough to answer queries before a live scrape.

## Auth

All query routes require:

```
X-API-Key: mf_live_…
```

`GET /health` is public.

```bash
python -m app.keys create --name grok-voice   # prints the key once
python -m app.keys list
python -m app.keys revoke --name grok-voice
```

Only the SHA-256 hash is stored. Never commit plaintext keys. On Railway, set `MF_API_KEY` in Variables (or mint a key after first boot and keep it in Variables).

## Zip then title

```bash
export KEY=mf_live_replace_me

curl -s -H "X-API-Key: $KEY" http://127.0.0.1:8000/zips/10023
curl -s -H "X-API-Key: $KEY" "http://127.0.0.1:8000/movies/search?q=the%20odysy&zip_code=10023"
curl -s -H "X-API-Key: $KEY" "http://127.0.0.1:8000/showtimes?movie_id=the-odyssey&zip_code=10023&date=today"
```

| operationId | method | path |
|---|---|---|
| `health` | GET | `/health` |
| `get_meta` | GET | `/meta` |
| `resolve_zip` | GET | `/zips/{zip_code}` |
| `list_movies` | GET | `/movies` |
| `search_movies` | GET | `/movies/search?q=` |
| `get_movie` | GET | `/movies/{movie_id}` |
| `list_theaters` | GET | `/theaters` |
| `get_showtimes` | GET | `/showtimes` |
| `ingest_snapshot` | POST | `/ingest/snapshots` |

OpenAPI: `http://127.0.0.1:8000/openapi.json` (public, no secrets).

Non-Manhattan ZIPs return `404` with `"code": "OUT_OF_AREA"`.

## Refresh listings

The voice agent reads the live Railway database. After a scrape, push the snapshot:

```bash
python -m ingest.refresh --source file --from-file data/snapshots/seed.json
python -m ingest.refresh --source fandango --post-url https://web-production-b3a9ce.up.railway.app
```

`POST /ingest/snapshots` (same `X-API-Key`) loads the JSON into the running process. Query routes see the new rows as soon as that call returns 200. Still commit the snapshot on `main` so the next deploy does not revert to an older file.

Live Fandango fetch is best-effort and must not invent rows. If a page cannot be parsed, last-good data stays loaded. See [docs/cloud-agent-refresh.md](docs/cloud-agent-refresh.md).

v1 roster: AMC and Regal houses in Manhattan. Alamo Drafthouse Lower Manhattan is planned for v2.

## Host on Railway

1. New project → deploy from GitHub → `njm-cursor-x/mf-backend`.
2. Builder: **Dockerfile** (not Railpack).
3. **Custom Start Command must be set** to `python -m app.run`.
   Leaving it blank does **not** use the Dockerfile. Railway falls back to a
   cached detected command: `uvicorn … --port ${PORT:-8000}`. That is shell
   syntax. Railway runs it without a shell, so uvicorn treats the literal
   `${PORT:-8000}` as the port and exits.
4. Variables: `MF_API_KEY=mf_live_…` (use a minted key).
5. Public domain target port: **8080** (Railway `$PORT`), not 80.
6. Confirm deploy logs print `mf-backend run.py listening on 0.0.0.0:…`
   then `Uvicorn running`. Then `GET https://<your-app>.up.railway.app/health`.

This is a long-lived process, not GitHub Pages or Vercel.

## Tests

```bash
pytest -q
```
