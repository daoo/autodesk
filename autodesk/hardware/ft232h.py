from autodesk.hardware.error import HardwareError
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H


class DeviceWrapper:
    def __init__(self):
        FT232H.use_FT232H()
        self.device = FT232H.FT232H()
        self.pins = []

    def add(self, pin, setup):
        self.pins.append((pin, setup))
        self.device.setup(pin, setup)

    def reconnect(self):
        FT232H.use_FT232H()
        self.device = FT232H.FT232H()
        for (pin, setup) in self.pins:
            self.device.setup(pin, setup)

    def close(self):
        self.device.close()

    def output(self, pin, value):
        try:
            self.device.output(pin, value)
        except RuntimeError:
            try:
                self.reconnect()
                self.device.output(pin, value)
            except RuntimeError as error:
                raise HardwareError(error)


class Ft232hOutputPin:
    def __init__(self, session, pin):
        self.session = session
        self.pin = pin

    def write(self, value):
        if value != 0 and value != 1:
            raise ValueError(
                'Pin value must be 0 or 1 but got {0}'.format(value))
        gpio_value = GPIO.LOW if value == 0 else GPIO.HIGH
        self.session.output(self.pin, gpio_value)


class Ft232hPinFactory:
    def __enter__(self):
        self.session = DeviceWrapper()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def create(self, pin):
        self.session.add(pin, GPIO.OUT)
        return Ft232hOutputPin(self.session, pin)
