from datetime import date, datetime

from pydantic import BaseModel, Field


class TheaterSummary(BaseModel):
    id: str = Field(examples=["amc-lincoln-square-13"])
    name: str = Field(examples=["AMC Lincoln Square 13"])
    chain: str = Field(examples=["AMC"])
    address: str = Field(examples=["1998 Broadway, New York, NY 10023"])
    zip_code: str = Field(examples=["10023"])
    neighborhood: str = Field(examples=["Lincoln Square"])


class MovieSummary(BaseModel):
    id: str = Field(examples=["the-odyssey"])
    title: str = Field(examples=["The Odyssey"])
    rating: str = Field(examples=["PG-13"])
    runtime_min: int = Field(examples=[150])
    synopsis: str = Field(examples=["Odysseus fights his way home."])
    score: int | None = Field(
        default=None,
        examples=[94],
        description="Spoken-title match score 0-100. Present on search only.",
    )


class ShowtimeItem(BaseModel):
    starts_at: datetime = Field(examples=["2026-09-11T19:45:00"])
    starts_at_local: str = Field(examples=["7:45 PM"])
    format: str = Field(examples=["IMAX"])


class TheaterShowtimes(BaseModel):
    theater: TheaterSummary
    times: list[ShowtimeItem]


class ZipResolved(BaseModel):
    zip_code: str = Field(examples=["10023"])
    neighborhood: str = Field(examples=["Lincoln Square"])
    borough: str = Field(examples=["Manhattan"])
    theaters: list[TheaterSummary]


class MovieList(BaseModel):
    date: date
    zip_code: str | None = None
    movies: list[MovieSummary]


class MovieSearch(BaseModel):
    query: str
    matches: list[MovieSummary]


class ShowtimeResponse(BaseModel):
    movie: MovieSummary
    date: date
    theaters: list[TheaterShowtimes]


class MetaResponse(BaseModel):
    app: str
    timezone: str
    as_of: datetime | None
    ingest_status: str | None
    theater_count: int
    movie_count: int
    showtime_count: int


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    api_key_configured: bool = Field(
        examples=[True],
        description="True when MF_API_KEY is set in the process env. Does not reveal the key.",
    )
    commit: str = Field(
        default="",
        examples=["6bcf742"],
        description="Short git SHA from RAILWAY_GIT_COMMIT_SHA when hosted.",
    )
