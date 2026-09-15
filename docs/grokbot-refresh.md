# GrokBot showtimes refresh

You are the fetch path for MovieFone Manhattan. You use the **Fandango website like a person**. You do not curl theater URLs from a script. You do not write SQLite. You produce a snapshot JSON and POST it to the showtimes API.

This is an unofficial demo. Not affiliated with MovieFone, Fandango, AMC, or Regal.

## Why the UI, not a saved URL

Fandango changes slugs and theater-page paths. A bookmark in `data/theaters.json` (`source_url`) is a **hint**, not the source of truth.

The source of truth is the **roster of 12 houses by name and Manhattan address**. Find those houses in the Fandango UI. If the URL behind a house changed, still scrape it, and note the new URL in your report.

Do **not** scrape “movies near me,” a ZIP, a borough homepage, or whatever Fandango promotes today. That will pull Brooklyn, NJ, and houses we do not serve.

## Closed roster (v1)

Only these theaters. Match **name + city**. If Fandango shows a similarly named house in another borough, skip it.

| id | name | address |
|---|---|---|
| `amc-empire-25` | AMC Empire 25 | 234 W 42nd St, New York, NY 10036 |
| `amc-lincoln-square-13` | AMC Lincoln Square 13 | 1998 Broadway, New York, NY 10023 |
| `amc-34th-street-14` | AMC 34th Street 14 | 312 W 34th St, New York, NY 10001 |
| `amc-kips-bay-15` | AMC Kips Bay 15 | 570 2nd Ave, New York, NY 10016 |
| `amc-village-7` | AMC Village 7 | 66 3rd Ave, New York, NY 10003 |
| `amc-19th-st-east-6` | AMC 19th St. East 6 | 890 Broadway, New York, NY 10003 |
| `amc-84th-street-6` | AMC 84th Street 6 | 2310 Broadway, New York, NY 10024 |
| `amc-orpheum-7` | AMC Orpheum 7 | 1538 3rd Ave, New York, NY 10028 |
| `amc-magic-johnson-harlem` | AMC Magic Johnson Harlem 9 | 230 W 125th St, New York, NY 10027 |
| `regal-union-square` | Regal Union Square | 850 Broadway, New York, NY 10003 |
| `regal-e-walk` | Regal E-Walk 13 | 247 W 42nd St, New York, NY 10036 |
| `regal-battery-park` | Regal Battery Park | 102 North End Ave, New York, NY 10282 |

Out of scope: Alamo Drafthouse, Brooklyn, Queens, Staten Island, NJ, any house not in this table.

## How to use the Fandango UI

For **each** roster row, in order:

1. Go to `https://www.fandango.com`.
2. Use site search or the theater finder. Type the **theater name** (e.g. `AMC Lincoln Square 13`).
3. Confirm the result’s address is the Manhattan address in the table (street + ZIP). If it is not, skip. Do not pick the closest other AMC.
4. Open that theater’s showtimes. Last-known `source_url` in `data/theaters.json` may be a shortcut; if it 404s or redirects to a different house, fall back to search.
5. Collect films and times for **today through the next 6 calendar days** in `America/New_York` (days `0`–`6`). If the UI only shows some of those days, include only the days you can see. Do not pad missing days with guessed times.
6. Record format as it appears: `IMAX`, `Dolby`, `standard` (use `standard` for 2D / no premium label).
7. Times as 24-hour `HH:MM` (`19:45`, not `7:45 PM`).

If you hit a captcha, bot wall, empty schedule, or an address mismatch: **skip that theater**. Do not retry into a different house. Do not invent rows.

A theater is all-or-nothing. If you only got Friday IMAX and not the rest of what the page showed, skip the whole theater. Do not merge half a day.

## Snapshot JSON

One object. Same shape as `data/snapshots/seed.json`.

- `source`: `"fandango"`
- `movies`: unique films you actually saw. `id` is a kebab slug of the title (`the-odyssey`). `title` is the billing title on the page. `rating`, `runtime_min`, `synopsis` if visible, else `""` / `0`.
- `showtimes`: one block per theater + movie + format.
  - `theater_id`: roster `id` only
  - `movie_id`: must exist in `movies`
  - `times`: at least one `HH:MM`
  - `days`: offsets from **today in America/New_York**. Today = `0`. Tomorrow = `1`.

Do not include a theater with zero times. If every theater was skipped, **do not POST**. Leave last-good data in place and report the skips.

## Load the live API

When Railway is up:

```bash
curl -sS -X POST \
  -H "X-API-Key: $MF_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @data/snapshots/YYYY-MM-DD.json \
  https://<railway-host>/ingest/snapshots

curl -sS -H "X-API-Key: $MF_API_KEY" \
  https://<railway-host>/meta
```

Pass only if `ingest_status` is `ok`. Unknown `theater_id` values return `400` — fix the id, do not coerce to a nearby house.

You do not restart or redeploy Railway. The POST is the live load.

Save the JSON under `data/snapshots/YYYY-MM-DD.json` and open a PR if the snapshot is new. That is durability for the next deploy. Do not commit API keys.

## Cadence

Twice a week (Monday and Thursday). One pass over all 12 houses. Do not scrape more often.

## Report

List: theaters ok, theaters skipped (reason), movie count, showtime count, `/meta` `as_of`. If you discovered a new Fandango URL for a roster house, include it so `source_url` can be updated later.
