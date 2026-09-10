from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Theater(Base):
    __tablename__ = "theaters"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    chain: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    zip_code: Mapped[str] = mapped_column(String, nullable=False)
    neighborhood: Mapped[str] = mapped_column(String, nullable=False)
    source_url: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[int] = mapped_column(Integer, default=1)

    showtimes: Mapped[list["Showtime"]] = relationship(back_populates="theater")


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[str] = mapped_column(String, default="")
    runtime_min: Mapped[int] = mapped_column(Integer, default=0)
    synopsis: Mapped[str] = mapped_column(Text, default="")

    showtimes: Mapped[list["Showtime"]] = relationship(back_populates="movie")


class Showtime(Base):
    __tablename__ = "showtimes"
    __table_args__ = (
        UniqueConstraint(
            "theater_id",
            "movie_id",
            "starts_at",
            "format",
            name="uq_showtime",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    theater_id: Mapped[str] = mapped_column(ForeignKey("theaters.id"), nullable=False)
    movie_id: Mapped[str] = mapped_column(ForeignKey("movies.id"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    format: Mapped[str] = mapped_column(String, default="standard")

    theater: Mapped[Theater] = relationship(back_populates="showtimes")
    movie: Mapped[Movie] = relationship(back_populates="showtimes")


class ZipCode(Base):
    __tablename__ = "zips"

    zip_code: Mapped[str] = mapped_column(String, primary_key=True)
    neighborhood: Mapped[str] = mapped_column(String, nullable=False)
    borough: Mapped[str] = mapped_column(String, default="Manhattan")


class ZipTheater(Base):
    __tablename__ = "zip_theaters"

    zip_code: Mapped[str] = mapped_column(ForeignKey("zips.zip_code"), primary_key=True)
    theater_id: Mapped[str] = mapped_column(ForeignKey("theaters.id"), primary_key=True)


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    key_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class IngestRun(Base):
    __tablename__ = "ingest_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, default="")
    snapshot_path: Mapped[str] = mapped_column(String, default="")
    theaters_ok: Mapped[int] = mapped_column(Integer, default=0)
    theaters_failed: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
