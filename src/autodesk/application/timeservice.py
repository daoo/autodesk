from datetime import UTC, datetime

MIN_TIME = datetime(1970, 1, 1, tzinfo=UTC)


class TimeService:
    @property
    def min(self) -> datetime:
        return MIN_TIME

    def now(self) -> datetime:
        return datetime.now(UTC)
