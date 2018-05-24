from datetime import time
import logging


class Operation:
    def __init__(self):
        self.logger = logging.getLogger('operation')
        self.allowance_start = time(8, 0, 0)
        self.allowance_end = time(18, 0, 0)

    def allowed(self, at):
        monday = 0
        friday = 4
        time_at = time(at.hour, at.minute, at.second)
        weekday = at.weekday()
        return \
            time_at >= self.allowance_start and \
            time_at <= self.allowance_end and \
            weekday >= monday and weekday <= friday
