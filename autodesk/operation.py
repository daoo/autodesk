import logging
from datetime import time

from autodesk.states import ACTIVE


class Operation:
    def __init__(self):
        self.logger = logging.getLogger("operation")
        self.allowance_start = time(7, 0, 0)
        self.allowance_end = time(20, 0, 0)

    def allowed(self, session_state, at):
        return session_state == ACTIVE and self._check_time(at)

    def _check_time(self, at):
        monday = 0
        friday = 4
        time_at = time(at.hour, at.minute, at.second)
        weekday = at.weekday()
        return (
            time_at >= self.allowance_start
            and time_at <= self.allowance_end
            and weekday >= monday
            and weekday <= friday
        )
