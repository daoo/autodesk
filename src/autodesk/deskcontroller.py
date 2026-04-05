import time

from autodesk.hardware.types import OutputPin
from autodesk.states import Desk


class DeskController:
    def __init__(
        self,
        delay: float,
        pin_down: OutputPin,
        pin_up: OutputPin,
        pin_light: OutputPin,
    ):
        self.delay = delay
        self.pin_down = pin_down
        self.pin_up = pin_up
        self.pin_light = pin_light

    def move(self, state: Desk) -> None:
        pin = self.pin_up if state.is_up else self.pin_down
        self.pin_light.write(1)
        pin.write(1)
        time.sleep(self.delay)
        pin.write(0)
        self.pin_light.write(0)
