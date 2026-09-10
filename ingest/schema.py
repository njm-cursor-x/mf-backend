from pydantic import BaseModel, Field


class SnapshotMovie(BaseModel):
    id: str
    title: str
    rating: str = ""
    runtime_min: int = 0
    synopsis: str = ""


class SnapshotShowtime(BaseModel):
    theater_id: str
    movie_id: str
    format: str = "standard"
    times: list[str] = Field(min_length=1)
    days: list[int] = Field(default_factory=lambda: [0])


class Snapshot(BaseModel):
    source: str = "unknown"
    movies: list[SnapshotMovie] = Field(min_length=1)
    showtimes: list[SnapshotShowtime] = Field(min_length=1)

    def theater_ids(self) -> set[str]:
        return {row.theater_id for row in self.showtimes}
