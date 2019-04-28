from autodesk.application import Application
from autodesk.hardware import create_hardware
from autodesk.model import Model
from autodesk.operation import Operation
from autodesk.sqlitedatastore import Sqlite3DataStore
from autodesk.timer import Timer


class ApplicationFactory:
    def __init__(self, database_path, hardware_kind, limits, delay, motor_pins,
                 light_pin):
        self.database_path = database_path
        self.hardware_kind = hardware_kind
        self.limits = limits
        self.delay = delay
        self.motor_pins = motor_pins
        self.light_pin = light_pin

    def create(self, loop):
        operation = Operation()
        timer = Timer(loop)
        model = Model(Sqlite3DataStore(self.database_path))
        hardware = create_hardware(
            self.hardware_kind,
            self.delay,
            self.motor_pins,
            self.light_pin)
        return Application(model, timer, hardware, operation, self.limits)
