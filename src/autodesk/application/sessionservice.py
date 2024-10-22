import logging

from autodesk.application.timeservice import TimeService
from autodesk.hardware.error import HardwareError
from autodesk.lightcontroller import LightController
from autodesk.model import Model
from autodesk.states import Session


class SessionService:
    def __init__(
        self, model: Model, light_controller: LightController, time_service: TimeService
    ):
        self.logger = logging.getLogger("sessionservice")
        self.model = model
        self.light_controller = light_controller
        self.time_service = time_service

    def init(self):
        state = self.model.get_session_state()
        self.light_controller.set(state)

    def get(self):
        return self.model.get_session_state()

    def get_active_time(self):
        return self.model.get_active_time(
            self.time_service.min, self.time_service.now()
        )

    def compute_hourly_count(self):
        return self.model.compute_hourly_count(
            self.time_service.min, self.time_service.now()
        )

    def set(self, state: Session):
        now = self.time_service.now()
        self.model.set_session(now, state)
        try:
            self.light_controller.set(state)
        except HardwareError as error:
            self.logger.warning("hardware failure, could not set session light")
            self.logger.debug(error)
            raise
