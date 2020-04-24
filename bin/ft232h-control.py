#!/usr/bin/env python
from pyftdi.i2c import I2cController
import sys
import time


def translate(gpio, pin, delay):
    pin_mask = gpio.pins | 1 << pin
    direction = gpio.direction | 1 << pin
    gpio.set_direction(pin_mask, direction)

    value = gpio.read(with_output=True)
    gpio.write((value | 1 << pin) & gpio.direction)
    time.sleep(delay)
    value = gpio.read(with_output=True)
    gpio.write(value & ~(1 << pin) & gpio.direction)


if len(sys.argv) != 3:
    sys.stderr.write('Usage: {0} pin delay\n'.format(sys.argv[0]))
    sys.exit(1)

pin = int(sys.argv[1])
delay = int(sys.argv[2])

controller = I2cController()
try:
    controller.configure("ftdi://ftdi:ft232h/1", frequency=1e6)
    gpio = controller.get_gpio()
    translate(gpio, pin, delay)
except ValueError:
    sys.stderr.write("Usage: {} PIN SECONDS\n".format(sys.argv[0]))
    sys.exit(1)
finally:
    controller.terminate()
