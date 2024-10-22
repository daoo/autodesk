from pandas import Timedelta

from autodesk.application.autodeskservice import AutoDeskService
from autodesk.application.deskservice import DeskService
from autodesk.application.sessionservice import SessionService
from autodesk.application.timeservice import TimeService
from autodesk.deskcontroller import DeskController
from autodesk.lightcontroller import LightController
from autodesk.model import Model
from autodesk.operation import Operation
from autodesk.scheduler import Scheduler
from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.timer import Timer


class AutoDeskServiceFactory:
    def __init__(
        self,
        database_path: str,
        pin_factory,
        limits: tuple[Timedelta, Timedelta],
        delay: float,
        motor_pins: tuple[int, int],
        light_pins: tuple[int, int],
    ):
        self.database_path = database_path
        self.pin_factory = pin_factory
        self.limits = limits
        self.delay = delay
        self.motor_pins = motor_pins
        self.light_pins = light_pins

    def create(self, loop):
        operation = Operation()
        timer = Timer(loop)
        model = Model(SqliteDataStore.open(self.database_path))
        scheduler = Scheduler(self.limits)
        desk_controller = DeskController(
            self.delay,
            self.pin_factory.create_output(self.motor_pins[0]),
            self.pin_factory.create_output(self.motor_pins[1]),
            self.pin_factory.create_output(self.light_pins[0]),
        )
        light_controller = LightController(
            self.pin_factory.create_output(self.light_pins[1])
        )
        timer_service = TimeService()
        session_service = SessionService(model, light_controller, timer_service)
        desk_service = DeskService(operation, model, desk_controller, timer_service)
        return AutoDeskService(
            operation, scheduler, timer, timer_service, session_service, desk_service
        )
