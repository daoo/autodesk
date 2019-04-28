from autodesk.hardware.error import HardwareError
from autodesk.spans import Event
from autodesk.states import INACTIVE
from datetime import datetime, timedelta
import logging


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

        time = datetime.now()
        if session.active() and self.operation.allowed(time):
            self._update_timer(
                time,
                self.model.get_desk_state(),
                self.model.get_session_state())

    def close(self):
        self.timer.cancel()
        self.model.close()
        self.hardware.close()

    def get_active_time(self):
        return self.model.get_active_time(datetime.min, datetime.now())

    def get_session_state(self):
        return self.model.get_session_state()

    def get_desk_state(self):
        return self.model.get_desk_state()

    def get_weekday_relative_frequency(self):
        return self.model.compute_hourly_relative_frequency(
            datetime.min, datetime.now())

    def set_session(self, session):
        time = datetime.now()
        try:
            self.hardware.light(session)
            self.model.set_session(Event(time, session))

            if session.active() and self.operation.allowed(time):
                self._update_timer(time, self.model.get_desk_state(), session)
            else:
                self.timer.cancel()
        except HardwareError:
            self.logger.warning('hardware failure, setting session inactive')
            self.model.set_session(Event(time, INACTIVE))
            self.timer.cancel()

    def set_desk(self, desk):
        time = datetime.now()
        if not self.operation.allowed(time):
            self.logger.warning('desk operation not allowed at this time')
            return False

        session = self.model.get_session_state()
        if not session.active():
            self.logger.warning('desk operation not allowed when inactive')
            return False

        try:
            self.hardware.desk(desk)
            self.model.set_desk(Event(time, desk))
            self._update_timer(time, desk, session)
        except HardwareError:
            self.logger.warning('hardware failure, not changing desk state')
            self.timer.cancel()
        return True

    def _compute_delay_to_next(self, time, desk):
        active_time = self.model.get_active_time(datetime.min, time)
        active_limit = desk.test(*self.limits)
        return max(timedelta(0), active_limit - active_time)

    def _update_timer(self, time, desk, session):
        self.timer.schedule(
            self._compute_delay_to_next(time, desk),
            lambda: self.set_desk(desk.next()))
