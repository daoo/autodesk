from autodesk.hardware.types import OutputPin
from autodesk.hardware.types import PinValue
from autodesk.states import Desk, Session


class LightController:
    def __init__(self, pin_session: OutputPin):
        self.pin_session = pin_session

    def set(self, state: Session | Desk) -> None:
        value: PinValue = state.test(0, 1)
        self.pin_session.write(value)
