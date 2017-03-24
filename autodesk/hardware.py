import time

try:
    import RPi.GPIO as GPIO
    DELAY = 15
except (ImportError, RuntimeError):
    DELAY = 0

    class GPIO:
        BOARD = "GPIO.BOARD"
        OUT = "GPIO.OUT"
        HIGH = "GPIO.HIGH"
        LOW = "GPIO.LOW"

        @staticmethod
        def setmode(input):
            print("Warning: GPIO not found, using test implementation.")
            print("GPIO.setmode({})".format(input))

        @staticmethod
        def setup(pin, state):
            print("GPIO.setup({}, {})".format(pin, state))

        @staticmethod
        def cleanup():
            print("GPIO.cleanup()")

        @staticmethod
        def output(pin, state):
            print("GPIO.output({}, {})".format(pin, state))

class Hardware:
    def __init__(self, pins):
        self.pins = pins

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)

    def cleanup(self):
        GPIO.cleanup()

    def go(self, state):
        pin = state.test(*self.pins)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(pin, GPIO.LOW)
