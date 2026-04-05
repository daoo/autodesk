from datetime import datetime, timezone

MIN_TIME = datetime(1970, 1, 1)
UTC = timezone.utc  # noqa: UP017


class TimeService:
    @property
    def min(self) -> datetime:
        return MIN_TIME.replace(tzinfo=UTC)

    def now(self) -> datetime:
        return datetime.now(UTC)
