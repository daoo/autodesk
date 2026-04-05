from autodesk.hardware.types import OutputPin, PinValue, validate_pin_value
from autodesk.states import Desk, Session


class LightController:
    def __init__(self, pin_session: OutputPin):
        self.pin_session = pin_session

    def set(self, state: Session | Desk) -> None:
        value: PinValue = validate_pin_value(1 if state.value else 0)
        self.pin_session.write(value)
