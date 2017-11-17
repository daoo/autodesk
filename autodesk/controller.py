from autodesk.spans import Event
from datetime import datetime, time, timedelta
import autodesk.stats as stats

DESK_OPERATION_ALLOWANCE_START = time(8, 0, 0)
DESK_OPERATION_ALLOWANCE_END = time(18, 0, 0)


def allow_desk_operation(at):
    monday = 0
    friday = 4
    time_at = time(at.hour, at.minute, at.second)
    weekday = at.weekday()
    return \
        time_at >= DESK_OPERATION_ALLOWANCE_START and \
        time_at <= DESK_OPERATION_ALLOWANCE_END and \
        weekday >= monday and weekday <= friday


class Controller:
    def __init__(self, hardware, limits, timer, database):
        self.hardware = hardware
        self.limits = limits
        self.timer = timer
        self.database = database

    def update_timer(self, time):
        if not allow_desk_operation(time):
            self.timer.stop()
            return

        beginning = datetime.fromtimestamp(0)
        session_spans = self.database.get_session_spans(beginning, time)
        if not session_spans[-1].data.active():
            self.timer.stop()
            return

        desk_spans = self.database.get_desk_spans(beginning, time)
        desk = desk_spans[-1].data
        active_time = stats.compute_active_time(session_spans, desk_spans)
        limit = desk.test(*self.limits)
        delay = max(timedelta(0), limit - active_time)
        self.timer.set(delay, desk.next())

    def set_session(self, time, state):
        self.database.insert_session_event(Event(time, state))
        self.hardware.setup()
        self.hardware.light(state)
        self.hardware.cleanup()
        self.update_timer(time)

    def set_desk(self, time, state):
        if not allow_desk_operation(time):
            self.update_timer(time)
            return False

        self.hardware.setup()
        self.hardware.go(state)
        self.hardware.cleanup()
        self.database.insert_desk_event(Event(time, state))
        self.update_timer(time)
        return True
