from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.dates import parse_query_date
from app.db import get_db
from app.errors import ApiError
from app.models import Movie, Showtime, Theater, ZipTheater
from app.schemas import MovieSummary, ShowtimeItem, ShowtimeResponse, TheaterSummary, TheaterShowtimes

router = APIRouter(tags=["showtimes"], dependencies=[Depends(require_api_key)])


def _theater_summary(theater: Theater) -> TheaterSummary:
    return TheaterSummary(
        id=theater.id,
        name=theater.name,
        chain=theater.chain,
        address=theater.address,
        zip_code=theater.zip_code,
        neighborhood=theater.neighborhood,
    )


@router.get(
    "/showtimes",
    operation_id="get_showtimes",
    summary="Showtimes for a movie",
    description="Required movie_id. Date defaults to today. Optional theater_id or zip_code. Times are America/New_York.",
    response_model=ShowtimeResponse,
)
def get_showtimes(
    movie_id: str = Query(..., examples=["the-odyssey"]),
    date: str | None = Query(None, examples=["today"]),
    theater_id: str | None = Query(None, examples=["amc-lincoln-square-13"]),
    zip_code: str | None = Query(None, examples=["10023"]),
    db: Session = Depends(get_db),
) -> ShowtimeResponse:
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise ApiError(404, "NOT_FOUND", "Unknown movie.", {"movie_id": movie_id})

    day = parse_query_date(date)
    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)

    query = select(Showtime).where(
        Showtime.movie_id == movie_id,
        Showtime.starts_at >= start,
        Showtime.starts_at < end,
    )
    if theater_id:
        query = query.where(Showtime.theater_id == theater_id)
    if zip_code:
        ids = list(
            db.scalars(select(ZipTheater.theater_id).where(ZipTheater.zip_code == zip_code))
        )
        if not ids:
            raise ApiError(
                404,
                "OUT_OF_AREA",
                "No listings for that ZIP. Coverage is Manhattan only.",
                {"zip_code": zip_code},
            )
        query = query.where(Showtime.theater_id.in_(ids))

    rows = list(db.scalars(query.order_by(Showtime.theater_id, Showtime.starts_at)))
    grouped: dict[str, list[Showtime]] = {}
    for row in rows:
        grouped.setdefault(row.theater_id, []).append(row)

    theaters_out: list[TheaterShowtimes] = []
    for tid, times in grouped.items():
        theater = db.get(Theater, tid)
        if theater is None:
            continue
        theaters_out.append(
            TheaterShowtimes(
                theater=_theater_summary(theater),
                times=[
                    ShowtimeItem(
                        starts_at=item.starts_at,
                        starts_at_local=item.starts_at.strftime("%I:%M %p").lstrip("0"),
                        format=item.format,
                    )
                    for item in times
                ],
            )
        )
    theaters_out.sort(key=lambda block: block.theater.name)
    return ShowtimeResponse(
        movie=MovieSummary(
            id=movie.id,
            title=movie.title,
            rating=movie.rating,
            runtime_min=movie.runtime_min,
            synopsis=movie.synopsis,
        ),
        date=day,
        theaters=theaters_out,
    )
