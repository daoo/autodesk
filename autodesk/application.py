from autodesk.hardware.error import HardwareError
from autodesk.states import INACTIVE, ACTIVE
from pandas import Timestamp
import logging


class Application:
    def __init__(self, model, timer, hardware, operation, scheduler):
        self.logger = logging.getLogger('application')
        self.model = model
        self.timer = timer
        self.hardware = hardware
        self.operation = operation
        self.scheduler = scheduler

    def init(self):
        session = self.model.get_session_state()
        self.hardware.light(session)

        time = Timestamp.now()
        if session == ACTIVE and self.operation.allowed(time):
            self._update_timer(
                self.model.get_active_time(Timestamp.min, time),
                self.model.get_desk_state())

    def close(self):
        self.timer.cancel()
        self.model.close()
        self.hardware.close()

    def get_active_time(self):
        return self.model.get_active_time(Timestamp.min, Timestamp.now())

    def get_session_state(self):
        return self.model.get_session_state()

    def get_desk_state(self):
        return self.model.get_desk_state()

    def compute_hourly_count(self):
        return self.model.compute_hourly_count(
            Timestamp.min, Timestamp.now())

    def set_session(self, session):
        time = Timestamp.now()
        try:
            self.hardware.light(session)
            self.model.set_session(time, session)

            if session == ACTIVE and self.operation.allowed(time):
                self._update_timer(
                    self.model.get_active_time(Timestamp.min, time),
                    self.model.get_desk_state())
            else:
                self.timer.cancel()
        except HardwareError:
            self.logger.warning('hardware failure, setting session inactive')
            self.model.set_session(time, INACTIVE)
            self.timer.cancel()

    def set_desk(self, desk):
        time = Timestamp.now()
        if not self.operation.allowed(time):
            self.logger.warning('desk operation not allowed at this time')
            return False

        session = self.model.get_session_state()
        if session == INACTIVE:
            self.logger.warning('desk operation not allowed when inactive')
            return False

        try:
            self.hardware.desk(desk)
            self.model.set_desk(time, desk)
            self._update_timer(
                self.model.get_active_time(Timestamp.min, time),
                desk)
        except HardwareError:
            self.logger.warning('hardware failure, not changing desk state')
            self.timer.cancel()
        return True

    def _update_timer(self, active_time, desk_state):
        self.timer.schedule(
            self.scheduler.compute_delay(active_time, desk_state),
            lambda: self.set_desk(desk_state.next()))
