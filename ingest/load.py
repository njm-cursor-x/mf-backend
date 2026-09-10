import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import DATA_DIR, SNAPSHOT_DIR
from app.dates import combine_local, today_local
from app.models import IngestRun, Movie, Showtime, Theater, ZipCode, ZipTheater
from ingest.schema import Snapshot


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sync_roster(db: Session) -> None:
    theaters = load_json(DATA_DIR / "theaters.json")
    zips = load_json(DATA_DIR / "zips.json")
    known_ids = {row["id"] for row in theaters}

    for row in theaters:
        theater = db.get(Theater, row["id"])
        if theater is None:
            theater = Theater(id=row["id"])
            db.add(theater)
        theater.name = row["name"]
        theater.chain = row["chain"]
        theater.address = row["address"]
        theater.zip_code = row["zip_code"]
        theater.neighborhood = row["neighborhood"]
        theater.source_url = row["source_url"]
        theater.active = 1

    db.execute(delete(ZipTheater))
    for row in zips:
        zip_row = db.get(ZipCode, row["zip_code"])
        if zip_row is None:
            zip_row = ZipCode(zip_code=row["zip_code"])
            db.add(zip_row)
        zip_row.neighborhood = row["neighborhood"]
        zip_row.borough = "Manhattan"
        for theater_id in row["theaters"]:
            if theater_id in known_ids:
                db.add(ZipTheater(zip_code=row["zip_code"], theater_id=theater_id))
    db.flush()


def apply_snapshot(db: Session, snapshot: Snapshot, snapshot_path: str, source: str) -> IngestRun:
    started = datetime.now(timezone.utc).replace(tzinfo=None)
    movies_by_id = {movie.id: movie for movie in snapshot.movies}
    for movie in snapshot.movies:
        row = db.get(Movie, movie.id)
        if row is None:
            row = Movie(id=movie.id)
            db.add(row)
        row.title = movie.title
        row.rating = movie.rating
        row.runtime_min = movie.runtime_min
        row.synopsis = movie.synopsis

    theater_ids = snapshot.theater_ids()
    missing = [tid for tid in theater_ids if db.get(Theater, tid) is None]
    if missing:
        raise ValueError(f"unknown theater ids in snapshot: {missing}")

    if theater_ids:
        db.execute(delete(Showtime).where(Showtime.theater_id.in_(theater_ids)))

    today = today_local()
    count = 0
    for block in snapshot.showtimes:
        if block.movie_id not in movies_by_id:
            raise ValueError(f"unknown movie_id {block.movie_id}")
        for day in block.days:
            show_date = today + timedelta(days=day)
            for hhmm in block.times:
                db.add(
                    Showtime(
                        theater_id=block.theater_id,
                        movie_id=block.movie_id,
                        starts_at=combine_local(show_date, hhmm),
                        format=block.format,
                    )
                )
                count += 1

    run = IngestRun(
        started_at=started,
        finished_at=datetime.now(timezone.utc).replace(tzinfo=None),
        status="ok",
        source=source,
        snapshot_path=snapshot_path,
        theaters_ok=len(theater_ids),
        theaters_failed=0,
        notes=f"loaded {count} showtimes",
    )
    db.add(run)
    db.commit()
    return run


def latest_snapshot_path() -> Path:
    dated = sorted(SNAPSHOT_DIR.glob("20*.json"))
    if dated:
        return dated[-1]
    seed = SNAPSHOT_DIR / "seed.json"
    if seed.exists():
        return seed
    raise FileNotFoundError("no snapshot files under data/snapshots")


def load_snapshot_file(db: Session, path: Path) -> IngestRun:
    snapshot = Snapshot.model_validate(load_json(path))
    return apply_snapshot(db, snapshot, str(path), snapshot.source)


def bootstrap_if_empty(db: Session) -> None:
    sync_roster(db)
    db.commit()
    if db.scalar(select(Showtime.id).limit(1)) is None:
        load_snapshot_file(db, latest_snapshot_path())
