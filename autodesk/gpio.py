try:
    from RPi.GPIO import BOARD, OUT, HIGH, LOW, setmode, setup, cleanup, output
except RuntimeError:
    BOARD = "GPIO.BOARD"
    OUT = "GPIO.OUT"
    HIGH = "GPIO.HIGH"
    LOW = "GPIO.LOW"

    def setmode(input):
        print("Warning: GPIO not found, using test implementation.")
        print("GPIO.setmode({})".format(input))

    def setup(pin, state):
        print("GPIO.setup({}, {})".format(pin, state))

    def cleanup():
        print("GPIO.cleanup()")

    def output(pin, state):
        print("GPIO.output({}, {})".format(pin, state))
