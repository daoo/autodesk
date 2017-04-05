from autodesk.spans import Event
from datetime import datetime, time, timedelta

DESK_OPERATION_ALLOWANCE_START = time(9, 0, 0)
DESK_OPERATION_ALLOWANCE_END = time(17, 0, 0)


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
        snapshot = self.database.get_snapshot(
            initial=datetime.fromtimestamp(0),
            final=time)
        if not allow_desk_operation(time):
            self.timer.stop()
        elif not snapshot.get_latest_session_state().active():
            self.timer.stop()
        else:
            desk = snapshot.get_latest_desk_state()
            active_time = snapshot.get_active_time()
            limit = desk.test(*self.limits)
            delay = max(timedelta(0), limit - active_time)
            self.timer.set(delay, desk.next())

    def set_session(self, time, state):
        self.database.insert_session_event(Event(time, state))
        self.update_timer(time)

    def set_desk(self, time, state):
        if allow_desk_operation(time):
            self.hardware.setup()
            self.hardware.go(state)
            self.hardware.cleanup()
            self.database.insert_desk_event(Event(time, state))

        self.update_timer(time)
