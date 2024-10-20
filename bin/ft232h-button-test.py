#!/usr/bin/env python
import time

from pyftdi.gpio import GpioMpsseController

pin = 4
delay = 0.1
controller = GpioMpsseController()
try:
    controller.configure("ftdi://ftdi:ft232h/1", frequency=1e6, direction=0x0000)
    gpio = controller.get_gpio()
    while True:
        print(gpio.read()[0] >> pin & 1)  # type: ignore
        time.sleep(delay)
finally:
    controller.close()
