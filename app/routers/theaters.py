from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.dates import parse_query_date
from app.db import get_db
from app.errors import ApiError
from app.models import Showtime, Theater, ZipTheater
from app.schemas import TheaterSummary

router = APIRouter(tags=["theaters"], dependencies=[Depends(require_api_key)])


def as_summary(theater: Theater) -> TheaterSummary:
    return TheaterSummary(
        id=theater.id,
        name=theater.name,
        chain=theater.chain,
        address=theater.address,
        zip_code=theater.zip_code,
        neighborhood=theater.neighborhood,
    )


@router.get(
    "/theaters",
    operation_id="list_theaters",
    summary="List theaters",
    description="Optional ZIP or movie_id. Date filters which houses are actually playing that movie.",
    response_model=list[TheaterSummary],
)
def list_theaters(
    zip_code: str | None = Query(None, examples=["10023"]),
    movie_id: str | None = Query(None, examples=["the-odyssey"]),
    date: str | None = Query(None, examples=["today"]),
    db: Session = Depends(get_db),
) -> list[TheaterSummary]:
    query = select(Theater)
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
        query = query.where(Theater.id.in_(ids))
    if movie_id:
        day = parse_query_date(date)
        start = f"{day.isoformat()} 00:00:00"
        end = f"{day.isoformat()} 23:59:59"
        playing = select(Showtime.theater_id).where(
            Showtime.movie_id == movie_id,
            Showtime.starts_at >= start,
            Showtime.starts_at <= end,
        )
        query = query.where(Theater.id.in_(playing))
    theaters = list(db.scalars(query.order_by(Theater.name)))
    return [as_summary(t) for t in theaters]
