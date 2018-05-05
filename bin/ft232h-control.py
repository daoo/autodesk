import Adafruit_GPIO.FT232H as FT232H
import sys
import time


def translate(pin, delay):
    FT232H.use_FT232H()
    device = FT232H.FT232H()

    device.setup(pin, FT232H.GPIO.OUT)

    device.output(pin, FT232H.GPIO.HIGH)
    time.sleep(delay)
    device.output(pin, FT232H.GPIO.LOW)
    device.close()


try:
    pin = int(sys.argv[1])
    delay = int(sys.argv[2])
    translate(pin, delay)
except ValueError:
    sys.stderr.write("Usage: {} PIN SECONDS\n".format(sys.argv[0]))
    sys.exit(1)
