from autodesk.application.autodeskservice import AutoDeskService
from autodesk.hardware.types import InputPin


class Button:
    def __init__(self, pin: InputPin, autodeskservice: AutoDeskService) -> None:
        self.pin = pin
        self.autodeskservice = autodeskservice
        self._button_down = False

    def poll(self) -> None:
        value = self.pin.read()
        if value == 1 and not self._button_down:
            self.autodeskservice.toggle_session()
            self._button_down = True
        elif value == 0:
            self._button_down = False
