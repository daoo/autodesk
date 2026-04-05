from datetime import timedelta

from autodesk.states import Desk


class Scheduler:
    def __init__(self, limits: tuple[timedelta, timedelta]):
        self.limits = limits

    def compute_delay(self, active_time: timedelta, desk_state: Desk) -> timedelta:
        active_limit = desk_state.test(*self.limits)
        return max(timedelta(0), active_limit - active_time)
