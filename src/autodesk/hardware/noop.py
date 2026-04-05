from autodesk.hardware.types import InputPin, OutputPin, PinFactory, PinValue


class NoopPin(InputPin, OutputPin):
    def __init__(self, pin: int):
        self.pin = pin

    def read(self) -> PinValue:
        return 0

    def write(self, value: PinValue) -> None:
        pass


class NoopPinFactory(PinFactory):
    def close(self) -> None:
        pass

    def create_input(self, pin: int) -> NoopPin:
        return NoopPin(pin)

    def create_output(self, pin: int) -> NoopPin:
        return NoopPin(pin)
