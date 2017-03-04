from autodesk.spans import Event
from datetime import datetime, time
import autodesk.hardware as hardware
import autodesk.model as model

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
    def __init__(self, timer_path, database):
        self.timer_path = timer_path
        self.database = database

    def update_timer(self, time):
        snapshot = self.database.get_snapshot(initial=datetime.fromtimestamp(0), final=time)
        with open(self.timer_path, 'w') as timer_file:
            if not allow_desk_operation(time):
                timer_file.write('stop\n')
            elif snapshot.session_latest.data == model.SESSION_INACTIVE:
                timer_file.write('stop\n')
            else:
                (delay, target) = snapshot.get_next_state()
                timer_file.write('{} {}\n'.format(
                    int(max(0, delay.total_seconds())), target))

    def set_session(self, state, time):
        assert state in [model.SESSION_ACTIVE, model.SESSION_INACTIVE]
        self.database.insert_session_event(Event(time, state))
        self.update_timer(time)

    def set_desk(self, state, time):
        assert state in [model.STATE_DOWN, model.STATE_UP]

        if not allow_desk_operation(time):
            return False

        hardware.setup()
        if state == model.STATE_DOWN:
            hardware.go_to_bottom()
        elif state == model.STATE_UP:
            hardware.go_to_top()
        hardware.cleanup()
        self.database.insert_desk_event(Event(time, state))
        self.update_timer(time)

        return True
