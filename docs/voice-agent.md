# Grok Voice Agent — API contract

This repo is the lookup brain. The voice agent is the mouth. Keep those jobs separate.

You write the **script** (tone, jokes, confirmations). This file is what APIs to call and when. Paste both into the Grok Voice Agent: script + this contract. Point the agent’s HTTP tools at the live OpenAPI spec, not at a guessed URL list.

## Wire-up

- **Base URL:** `https://mf-backend-production.up.railway.app`
- **OpenAPI (public, no key):** `https://mf-backend-production.up.railway.app/openapi.json`
- **Auth on every query tool:** header `X-API-Key` = Railway `MF_API_KEY`. Prefer a secret field in the voice-agent product, not the spoken prompt.
- Import tools from that OpenAPI. Enable only:

  | operationId | when |
  |---|---|
  | `resolve_zip` | after the caller says a ZIP |
  | `search_movies` | after they say a movie title |
  | `get_showtimes` | after they confirm a movie |
  | `get_movie` | optional, if you need a clean title read-back |
  | `get_meta` | once at call start, or if listings sound stale |

  Do **not** enable `ingest_snapshot`, `list_movies` as the main path, or anything that writes. The caller never loads the database.

## Call order (do not skip)

Classic MovieFone: **ZIP, then title, then times.** No keypad. No “first three letters.”

1. Optional: `GET /meta`. If `ingest_status` is not `ok`, say listings may be stale. Do not invent times.
2. Hear a 5-digit ZIP. `GET /zips/{zip_code}`.
   - `200`: use `neighborhood` in the confirm (“Lincoln Square”). Remember `zip_code`.
   - `404` + `code: OUT_OF_AREA`: not Manhattan. Say so. Do not search movies.
   - Bad ZIP (4 digits, “a hundred twenty three” you cannot parse): ask again. Do not call the API.
3. Hear a movie name. `GET /movies/search?q={what they said}&zip_code={zip}&date=today`.
   - Use `q` as the raw spoken title (`the odysy` is fine).
   - Always pass `zip_code` so matches are films playing near them.
4. Read `matches`:
   - One clear hit (high `score`, obvious title): confirm that `title`, keep `id`.
   - Two or three plausible hits: ask which one. Do not pick silently.
   - Duplicate titles (`The Odyssey` and `The Odyssey (2026)`): prefer the one with times you will actually read, usually the `*-2026` scrape id if both appear. Confirm the title once, not both ids.
   - Empty: say you do not have that title in Manhattan tonight. Offer another title. Do not guess a nearby film.
5. `GET /showtimes?movie_id={id}&zip_code={zip}&date=today`.
   - `date` is `today`, `tomorrow`, or `YYYY-MM-DD` if they asked a day.
   - Read theater **name** and times from `starts_at_local` (already Eastern). Do not convert UTC yourself.
   - If they name a house, you may add `theater_id` (roster id like `amc-lincoln-square-13`). If you are not sure, omit it and filter by `zip_code`.
6. If they change ZIP or movie, start again from that step. Do not reuse an old `movie_id` with a new ZIP without searching again.

## What you never do

- Invent a showtime, theater, or rating.
- Call Fandango.
- Call `POST /ingest/snapshots`.
- Tell the caller an API path, status code, or movie id.
- Claim this is official MovieFone / Fandango / AMC / Regal.

## Errors

JSON errors look like `{"code":"…","message":"…","details":{}}`.

| code | meaning | say |
|---|---|---|
| `OUT_OF_AREA` | ZIP not in the Manhattan map | No listings outside Manhattan. |
| `NOT_FOUND` | unknown movie or no times for that filter | Don’t have that one / no times for that day. |
| `UNAUTHORIZED` | missing or wrong key | Tools are misconfigured. Do not debug on the call. |

## Script vs tools

The script owns: greeting, how you ask for ZIP and title, how you read a 7:45, whether you offer tomorrow. This file owns: which `operationId` fires after each answer. If the script and this contract disagree on order, this contract wins.
