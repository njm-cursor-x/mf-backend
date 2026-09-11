# Weekly showtimes refresh

Run this as a Cursor cloud agent **once or twice a week** (Thursday evening or Friday morning, optional mid-week). This agent refreshes data. It does not host the API.

The voice agent reads the **live Railway process**. A git commit alone is not enough. After a refresh, **POST the snapshot** to the API, confirm `/meta`, then commit the file so the next Railway deploy does not revert.

## What to do

1. Work in `njm-cursor-x/mf-backend`.
2. Run (set `MF_API_KEY` to the same key as Railway):

```bash
python -m ingest.refresh --source fandango --post-url https://web-production-b3a9ce.up.railway.app
```

3. The CLI writes/keeps a snapshot under `data/snapshots/`, then `POST /ingest/snapshots`. The live SQLite updates immediately. Voice queries use the new rows as soon as that POST returns 200.
4. Confirm:

```bash
curl -s -H "X-API-Key: $MF_API_KEY" https://web-production-b3a9ce.up.railway.app/meta
```

`ingest_status` must be `ok`. That is the pass/fail for the job. Voice routes using last-good seed after a Fandango block is a **successful** run, not a failure.
5. If Fandango returns HTML and the page shape changed, **fix only `ingest/fandango.py`**. Do not invent showtimes. Do not write freeform rows into SQLite.
6. If the live fetch fails (Akamai 403 from a cloud IP is expected), the CLI keeps the last-good snapshot and still POSTs that. Report which theater IDs failed. Do not treat that as a job failure when `/meta` is `ok`.
7. Commit a new snapshot JSON only when one was written. Do not commit plaintext API keys. Railway auto-deploys `main`; the commit is durability, not the live load.

## Rules

- Roster is `data/theaters.json`. Do not scrape by ZIP.
- v1 is AMC + Regal Manhattan majors only. Alamo Drafthouse Lower Manhattan is v2 (`drafthouse.com`), not this job.
- A partial theater payload is a failure for that theater. Skip it. Do not merge half a day of times.
- Empty results after a failed ingest are not acceptable — last-good data must remain queryable.
- Do not call Railway `redeploy` after a refresh. That reuses the old image.

## Reload without Fandango

```bash
python -m ingest.refresh --source file --from-file data/snapshots/seed.json --post-url https://web-production-b3a9ce.up.railway.app
```
