"""Refresh Manhattan showtimes from a snapshot file or a live source."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.config import DATA_DIR
from app.db import SessionLocal, init_db
from ingest.fandango import fetch_theater
from ingest.load import latest_snapshot_path, load_json, load_snapshot_file, sync_roster


def refresh_from_file(path: Path) -> None:
    init_db()
    with SessionLocal() as db:
        sync_roster(db)
        db.commit()
        run = load_snapshot_file(db, path)
        print(f"{run.status} source={run.source} {run.notes} file={path}")


def refresh_from_fandango() -> int:
    init_db()
    theaters = load_json(DATA_DIR / "theaters.json")
    failed: list[str] = []
    fetched = 0
    for row in theaters:
        result = fetch_theater(row["source_url"], row["id"])
        if not result.ok:
            failed.append(f"{row['id']}: {result.error}")
            continue
        fetched += 1
        # Parser is intentionally strict: unmapped HTML must not become rows.
        failed.append(f"{row['id']}: page fetched but extractor is not mapped")

    print(f"fetched={fetched} failed={len(failed)}")
    for line in failed:
        print(f"  skip {line}")

    last = latest_snapshot_path()
    print(f"keeping last-good snapshot: {last}")
    refresh_from_file(last)
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh the showtimes snapshot")
    parser.add_argument("--source", choices=["fandango", "file"], default="file")
    parser.add_argument("--from-file", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.source == "file" or args.from_file:
        path = args.from_file or latest_snapshot_path()
        refresh_from_file(path)
        return 0
    return refresh_from_fandango()


if __name__ == "__main__":
    raise SystemExit(main())
