from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.dates import parse_query_date
from app.db import get_db
from app.errors import ApiError
from app.models import Movie, Showtime, ZipTheater
from app.schemas import MovieList, MovieSearch, MovieSummary
from app.search import rank_movies

router = APIRouter(tags=["movies"], dependencies=[Depends(require_api_key)])


def movie_summary(movie: Movie, score: int | None = None) -> MovieSummary:
    return MovieSummary(
        id=movie.id,
        title=movie.title,
        rating=movie.rating,
        runtime_min=movie.runtime_min,
        synopsis=movie.synopsis,
        score=score,
    )


def movies_for(db: Session, zip_code: str | None, day) -> list[Movie]:
    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)
    query = select(Movie).join(Showtime).where(
        Showtime.starts_at >= start,
        Showtime.starts_at < end,
    )
    if zip_code:
        theater_ids = list(
            db.scalars(select(ZipTheater.theater_id).where(ZipTheater.zip_code == zip_code))
        )
        if not theater_ids:
            raise ApiError(
                404,
                "OUT_OF_AREA",
                "No listings for that ZIP. Coverage is Manhattan only.",
                {"zip_code": zip_code},
            )
        query = query.where(Showtime.theater_id.in_(theater_ids))
    movies = list(db.scalars(query.distinct().order_by(Movie.title)))
    return movies


@router.get(
    "/movies",
    operation_id="list_movies",
    summary="Movies now playing",
    description="Optional ZIP filters to nearby theaters. Date is today if omitted.",
    response_model=MovieList,
)
def list_movies(
    zip_code: str | None = Query(None, examples=["10023"]),
    date: str | None = Query(None, examples=["today"]),
    db: Session = Depends(get_db),
) -> MovieList:
    day = parse_query_date(date)
    movies = movies_for(db, zip_code, day)
    return MovieList(
        date=day,
        zip_code=zip_code,
        movies=[movie_summary(m) for m in movies],
    )


@router.get(
    "/movies/search",
    operation_id="search_movies",
    summary="Spoken movie title search",
    description="Fuzzy match on the title the caller said. Returns a short ranked list when ambiguous.",
    response_model=MovieSearch,
)
def search_movies(
    q: str = Query(..., min_length=2, examples=["jurasic park"], description="Spoken title"),
    zip_code: str | None = Query(None, examples=["10023"]),
    date: str | None = Query(None, examples=["today"]),
    db: Session = Depends(get_db),
) -> MovieSearch:
    day = parse_query_date(date)
    catalog = movies_for(db, zip_code, day) or list(db.scalars(select(Movie)))
    ranked = rank_movies(q, catalog)
    return MovieSearch(
        query=q,
        matches=[movie_summary(movie, score) for score, movie in ranked],
    )


@router.get(
    "/movies/{movie_id}",
    operation_id="get_movie",
    summary="Confirm a movie",
    response_model=MovieSummary,
)
def get_movie(movie_id: str, db: Session = Depends(get_db)) -> MovieSummary:
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise ApiError(404, "NOT_FOUND", "Unknown movie.", {"movie_id": movie_id})
    return movie_summary(movie)
