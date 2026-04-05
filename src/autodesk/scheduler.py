from datetime import timedelta

from autodesk.states import Desk


class Scheduler:
    def __init__(self, limits: tuple[timedelta, timedelta]):
        self.limits = limits

    def compute_delay(self, active_time: timedelta, desk_state: Desk) -> timedelta:
        active_limit = self.limits[0] if desk_state.is_down else self.limits[1]
        return max(timedelta(0), active_limit - active_time)
