import logging

from autodesk.hardware.error import HardwareError


class DeskService:
    def __init__(self, operation, model, desk_controller, time_service):
        self.logger = logging.getLogger("deskservice")
        self.operation = operation
        self.model = model
        self.desk_controller = desk_controller
        self.time_service = time_service

    def get(self):
        return self.model.get_desk_state()

    def set(self, desk):
        now = self.time_service.now()
        session = self.model.get_session_state()
        if not self.operation.allowed(session, now):
            self.logger.warning("desk operation not allowed at this time")
            return

        try:
            self.desk_controller.move(desk)
            self.model.set_desk(self.time_service.now(), desk)
        except HardwareError as error:
            self.logger.error("hardware failure, desk state not updated in model")
            self.logger.debug(error)
            raise
