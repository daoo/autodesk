from pandas import Timedelta


class Scheduler:
    def __init__(self, limits: tuple[Timedelta, Timedelta]):
        self.limits = limits

    def compute_delay(self, active_time, desk_state):
        active_limit = desk_state.test(*self.limits)
        return max(Timedelta(0), active_limit - active_time)
