import RPi.GPIO as GPIO


class RaspberryPiOutputPin:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def write(self, value):
        if value != 0 and value != 1:
            raise ValueError(
                'Pin value must be 0 or 1 but got {0}'.format(value))
        gpio_value = GPIO.LOW if value == 0 else GPIO.HIGH
        GPIO.output(self.pin, gpio_value)


class RaspberryPiPinFactory:
    def __enter__(self):
        GPIO.setmode(GPIO.BOARD)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        GPIO.cleanup()

    def create(self, pin):
        return RaspberryPiOutputPin(pin)
