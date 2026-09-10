"""Best-effort Fandango theater-page fetch. Isolated from the query API."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

import httpx

USER_AGENT = (
    "Mozilla/5.0 (compatible; mf-backend-ingest/0.1; +https://github.com/njm-cursor-x/mf-backend)"
)


@dataclass
class TheaterFetch:
    theater_id: str
    ok: bool
    raw_html: str = ""
    error: str = ""


def fetch_theater(source_url: str, theater_id: str, timeout: float = 20.0) -> TheaterFetch:
    try:
        response = httpx.get(
            source_url,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
            follow_redirects=True,
            timeout=timeout,
        )
        response.raise_for_status()
        return TheaterFetch(theater_id=theater_id, ok=True, raw_html=response.text)
    except httpx.HTTPError as exc:
        return TheaterFetch(theater_id=theater_id, ok=False, error=str(exc))


def extract_json_blob(html: str) -> dict | None:
    """Look for a Next.js or JSON-LD payload. Returns None if the page shape changed."""
    next_data = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.S,
    )
    if next_data:
        try:
            return json.loads(next_data.group(1))
        except json.JSONDecodeError:
            return None
    ld_blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>',
        html,
        re.S,
    )
    for block in ld_blocks:
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue
    return None


def parse_theater_page(html: str) -> list[dict]:
    """Return raw show rows or raise if we cannot confidently parse."""
    blob = extract_json_blob(html)
    if blob is None:
        raise ValueError("no JSON payload on theater page")
    raise ValueError("Fandango page JSON shape not mapped yet; do not invent showtimes")
