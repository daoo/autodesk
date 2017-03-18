from autodesk.spans import Event
from datetime import datetime, time, timedelta
import autodesk.hardware as hardware

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
    def __init__(self, pins, limits, timer_path, database):
        self.pins = pins
        self.limits = limits
        self.timer_path = timer_path
        self.database = database

    def update_timer(self, time):
        snapshot = self.database.get_snapshot(
            initial=datetime.fromtimestamp(0),
            final=time)
        with open(self.timer_path, 'w') as timer_file:
            if not allow_desk_operation(time):
                timer_file.write('stop\n')
            elif not snapshot.session_latest.data.active():
                timer_file.write('stop\n')
            else:
                desk = snapshot.get_latest_desk_state()
                active_time = snapshot.get_active_time()
                limit = desk.test(*self.limits)
                delay = max(timedelta(0), limit - active_time)
                target = desk.next()
                timer_file.write('{} {}\n'.format(
                    int(max(0, delay.total_seconds())), target))

    def set_session(self, time, state):
        self.database.insert_session_event(Event(time, state))
        self.update_timer(time)

    def set_desk(self, time, state):
        if not allow_desk_operation(time):
            return False

        hardware.setup(*self.pins)
        hardware.go_to(state.test(*self.pins))
        hardware.cleanup()
        self.database.insert_desk_event(Event(time, state))
        self.update_timer(time)

        return True
