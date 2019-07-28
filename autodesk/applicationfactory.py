from autodesk.application.deskservice import DeskService
from autodesk.application.lightservice import LightService
from autodesk.application import Application
from autodesk.model import Model
from autodesk.operation import Operation
from autodesk.scheduler import Scheduler
from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.timer import Timer


class ApplicationFactory:
    def __init__(self, database_path, pin_factory, limits, delay, motor_pins,
                 light_pin):
        self.database_path = database_path
        self.pin_factory = pin_factory
        self.limits = limits
        self.delay = delay
        self.motor_pins = motor_pins
        self.light_pin = light_pin

    def create(self, loop):
        operation = Operation()
        timer = Timer(loop)
        model = Model(SqliteDataStore(self.database_path))
        scheduler = Scheduler(self.limits)
        desk_service = DeskService(
            self.delay,
            self.pin_factory.create(self.motor_pins[0]),
            self.pin_factory.create(self.motor_pins[1]))
        light_service = LightService(
            self.pin_factory.create(self.light_pin))
        return Application(
            model, timer, desk_service, light_service, operation, scheduler)
