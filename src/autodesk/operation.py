import logging
from datetime import datetime, time

from autodesk.states import Session


class Operation:
    def __init__(self) -> None:
        self.logger = logging.getLogger("operation")
        self.allowance_start = time(7, 0, 0)
        self.allowance_end = time(20, 0, 0)

    def allowed(self, session_state: Session, at: datetime) -> bool:
        return session_state.is_active and self._check_time(at)

    def _check_time(self, at: datetime) -> bool:
        monday = 0
        friday = 4
        time_at = at.time()
        weekday = at.weekday()
        return (
            time_at >= self.allowance_start
            and time_at <= self.allowance_end
            and weekday >= monday
            and weekday <= friday
        )
