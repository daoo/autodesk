class RPi:
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


import sys
sys.modules['RPi'] = RPi
sys.modules['RPi.GPIO'] = RPi.GPIO
from autodesk.webserver import app

app.config.update(dict(DELAY=0))

# Runs webserver with mocked GPIO for testing on non-raspberry computers.
