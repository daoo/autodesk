import logging

from autodesk.application.timeservice import TimeService
from autodesk.deskcontroller import DeskController
from autodesk.hardware.error import HardwareError
from autodesk.model import Model
from autodesk.operation import Operation
from autodesk.states import Desk


class DeskService:
    def __init__(
        self,
        operation: Operation,
        model: Model,
        desk_controller: DeskController,
        time_service: TimeService,
    ):
        self.logger = logging.getLogger("deskservice")
        self.operation = operation
        self.model = model
        self.desk_controller = desk_controller
        self.time_service = time_service

    def get(self) -> Desk:
        return self.model.get_desk_state()

    def operation_allowed(self) -> bool:
        now = self.time_service.now()
        session = self.model.get_session_state()
        return self.operation.allowed(session, now)

    def set(self, desk: Desk) -> bool:
        now = self.time_service.now()
        session = self.model.get_session_state()
        if not self.operation.allowed(session, now):
            self.logger.warning("desk operation not allowed at this time")
            return False

        try:
            self.desk_controller.move(desk)
            self.model.set_desk(now, desk)
            return True
        except HardwareError as error:
            self.logger.error("hardware failure, desk state not updated in model")
            self.logger.debug(error)
            raise
