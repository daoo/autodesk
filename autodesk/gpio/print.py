OUT = "GPIO.OUT"
HIGH = "GPIO.HIGH"
LOW = "GPIO.LOW"


def setup(pin, state):
    print("GPIO.setup({}, {})".format(pin, state))


def cleanup():
    print("GPIO.cleanup()")


def output(pin, state):
    print("GPIO.output({}, {})".format(pin, state))
