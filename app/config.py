from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mf_api_key: str = ""
    mf_db_path: Path = DATA_DIR / "showtimes.db"
    mf_tz: str = "America/New_York"
    mf_app_name: str = "MovieFone Manhattan Showtimes API"


settings = Settings()
