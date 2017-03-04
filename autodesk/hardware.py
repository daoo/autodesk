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

pinUp = 13
pinDown = 15


def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pinUp, GPIO.OUT)
    GPIO.setup(pinDown, GPIO.OUT)


def cleanup():
    GPIO.cleanup()


def go(pin, length):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(length)
    GPIO.output(pin, GPIO.LOW)


def go_to_top():
    go(pinUp, DELAY)

def go_to_bottom():
    go(pinDown, DELAY)
