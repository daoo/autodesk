import RPi.GPIO as GPIO  # type: ignore

from autodesk.hardware.types import InputPin, OutputPin, PinFactory, PinValue


class RaspberryPiInputPin(InputPin):
    def __init__(self, pin: int):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)

    def read(self) -> PinValue:
        gpio_value = GPIO.input(self.pin)
        value = 1 if gpio_value == GPIO.HIGH else 0
        return value


class RaspberryPiOutputPin(OutputPin):
    def __init__(self, pin: int):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def write(self, value: PinValue) -> None:
        if value != 0 and value != 1:
            raise ValueError(f"Pin value must be 0 or 1 but got {value}")
        gpio_value = GPIO.LOW if value == 0 else GPIO.HIGH
        GPIO.output(self.pin, gpio_value)


class RaspberryPiPinFactory(PinFactory):
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

    def close(self) -> None:
        GPIO.cleanup()

    def create_input(self, pin: int) -> RaspberryPiInputPin:
        return RaspberryPiInputPin(pin)

    def create_output(self, pin: int) -> RaspberryPiOutputPin:
        return RaspberryPiOutputPin(pin)
