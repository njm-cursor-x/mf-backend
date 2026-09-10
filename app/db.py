from collections.abc import Generator

from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Base, IngestRun


def _sqlite_url(path=settings.mf_db_path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


engine = create_engine(
    _sqlite_url(),
    connect_args={"check_same_thread": False},
)


def configure_engine(path) -> None:
    global engine, SessionLocal
    engine = create_engine(
        _sqlite_url(path),
        connect_args={"check_same_thread": False},
    )
    SessionLocal.configure(bind=engine)


@event.listens_for(Engine, "connect")
def _fk_on(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def latest_ingest(db: Session) -> IngestRun | None:
    return db.scalar(select(IngestRun).order_by(IngestRun.id.desc()).limit(1))
