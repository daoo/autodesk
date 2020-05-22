from autodesk.hardware.error import HardwareError
import logging


class AutoDeskService:
    def __init__(self, operation, scheduler, timer, time_service,
                 session_service, desk_service):
        self.logger = logging.getLogger('autodeskservice')
        self.operation = operation
        self.timer = timer
        self.scheduler = scheduler
        self.time_service = time_service
        self.session_service = session_service
        self.desk_service = desk_service

    def init(self):
        try:
            self.session_service.init()
            self._update_timer()
        except HardwareError as error:
            self.logger.warning('hardware failure, timer not started')
            self.logger.debug(error)
            self.timer.cancel()

    def get_session_state(self):
        return self.session_service.get()

    def set_session(self, state):
        try:
            self.session_service.set(state)
            self._update_timer()
        except HardwareError as error:
            self.logger.warning('hardware failure, timer cancelled')
            self.logger.debug(error)
            self.timer.cancel()

    def toggle_session(self):
        session_state = self.session_service.get()
        self.set_session(session_state.next())

    def get_desk_state(self):
        return self.desk_service.get()

    def set_desk(self, state):
        try:
            self.desk_service.set(state)
            self._update_timer()
        except HardwareError as error:
            self.logger.warning('hardware failure, timer cancelled')
            self.logger.debug(error)
            self.timer.cancel()

    def get_active_time(self):
        return self.session_service.get_active_time()

    def compute_hourly_count(self):
        return self.session_service.compute_hourly_count()

    def _update_timer(self):
        session_state = self.session_service.get()
        desk_state = self.desk_service.get()
        now = self.time_service.now()
        if self.operation.allowed(session_state, now):
            active_time = self.session_service.get_active_time()
            self.timer.schedule(
                self.scheduler.compute_delay(active_time, desk_state),
                lambda: self.set_desk(desk_state.next()))
        else:
            self.timer.cancel()
