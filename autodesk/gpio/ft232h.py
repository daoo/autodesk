from Adafruit_GPIO import OUT, HIGH, LOW
import FT232H


FT232H.use_FT232H()
device = FT232H.FT232H()


def setup(pin, state):
    device.setup(pin, state)


def cleanup():
    device.close()


def output(pin, state):
    device.output(pin, state)
