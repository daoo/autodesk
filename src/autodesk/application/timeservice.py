from datetime import datetime


class TimeService:
    @property
    def min(self) -> datetime:
        return datetime.min

    def now(self) -> datetime:
        return datetime.now()
