from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.config import settings
from app.errors import ApiError

TZ = ZoneInfo(settings.mf_tz)

RELATIVE_DATES = {"today", "tomorrow"}


def now_local() -> datetime:
    return datetime.now(TZ)


def today_local() -> date:
    return now_local().date()


def parse_query_date(value: str | None) -> date:
    if value is None or value == "today":
        return today_local()
    if value == "tomorrow":
        return today_local() + timedelta(days=1)
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ApiError(
            400,
            "INVALID_DATE",
            "date must be YYYY-MM-DD, today, or tomorrow.",
            {"date": value},
        ) from exc


def combine_local(day: date, hhmm: str) -> datetime:
    hour, minute = (int(part) for part in hhmm.split(":", 1))
    return datetime(day.year, day.month, day.day, hour, minute)
