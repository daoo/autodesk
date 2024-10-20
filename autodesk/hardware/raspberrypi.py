import RPi.GPIO as GPIO  # type: ignore


class RaspberryPiInputPin:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)

    def read(self):
        gpio_value = GPIO.input(self.pin)
        value = 1 if gpio_value == GPIO.HIGH else 0
        return value


class RaspberryPiOutputPin:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def write(self, value):
        if value != 0 and value != 1:
            raise ValueError(f"Pin value must be 0 or 1 but got {value}")
        gpio_value = GPIO.LOW if value == 0 else GPIO.HIGH
        GPIO.output(self.pin, gpio_value)


class RaspberryPiPinFactory:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

    def close(self):
        GPIO.cleanup()

    def create_input(self, pin):
        return RaspberryPiInputPin(pin)

    def create_output(self, pin):
        return RaspberryPiOutputPin(pin)
