# Weekly showtimes refresh

Run this as a Cursor cloud agent **once or twice a week** (Thursday evening or Friday morning, optional mid-week). This agent refreshes data. It does not host the API.

## What to do

1. Work in `njm-cursor-x/mf-backend` on a branch.
2. Run:

```bash
python -m ingest.refresh --source fandango
```

3. If Fandango pages still parse, the CLI writes `data/snapshots/YYYY-MM-DD.json` and loads SQLite.
4. If a theater page changed, **fix only `ingest/fandango.py`**. Do not invent showtimes. Do not write freeform rows into SQLite.
5. If the live fetch fails, the CLI keeps the last-good snapshot (`data/snapshots/seed.json` or the newest dated file) and loads that. Report which theater IDs failed.
6. Commit the new snapshot when it validates. Do not commit plaintext API keys.

## Rules

- Roster is `data/theaters.json`. Do not scrape by ZIP.
- v1 is AMC + Regal Manhattan majors only. Alamo Drafthouse Lower Manhattan is v2 (`drafthouse.com`), not this job.
- A partial theater payload is a failure for that theater. Skip it. Do not merge half a day of times.
- Empty results after a failed ingest are not acceptable — last-good data must remain queryable.

## Reload without the network

```bash
python -m ingest.refresh --source file --from-file data/snapshots/seed.json
```
