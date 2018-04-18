from autodesk.spans import Event
from datetime import datetime, time, timedelta
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

class Application:
    def __init__(self, model, timer, hardware, operation, limits):
        self.logger = logging.getLogger('application')
        self.model = model
        self.timer = timer
        self.hardware = hardware
        self.operation = operation
        self.limits = limits

    def init(self):
        session = self.model.get_session_state()
        self.hardware.light(session)

        if session.active() and self.operation.allowed(time):
            self._update_timer(
                datetime.now(),
                self.model.get_desk_state(),
                self.model.get_session_state())

    def close(self):
        self.timer.cancel()
        self.hardware.close()

    def set_session(self, time, session):
        self.model.set_session(Event(time, session))
        self.hardware.light(session)

        if session.active() and self.operation.allowed(time):
            self._update_timer(time, self.model.get_desk_state(), session)
        else:
            self.timer.cancel()

    def set_desk(self, time, desk):
        if not self.operation.allowed(time):
            self.logger.warning('desk operation not allowed at this time')
            return False

        session = self.model.get_session_state()
        if not session.active():
            self.logger.warning('desk operation not allowed when inactive')
            return False

        self.model.set_desk(Event(time, desk))
        self.hardware.desk(desk)
        self._update_timer(time, desk, session)
        return True

    def _update_timer(self, time, desk, session):
        active_time = self.model.get_active_time(datetime.min, time)
        limit = desk.test(*self.limits)
        delay = max(timedelta(0), limit - active_time)
        self.timer.schedule(delay, lambda: self.set_desk(datetime.now(), desk.next()))
