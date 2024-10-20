#!/usr/bin/env python
import time

from pyftdi.gpio import GpioMpsseController


def toggle(gpio, delay):
    gpio.write(0x0000 & gpio.direction)
    print("off", bin(gpio.read()[0]))
    time.sleep(delay)
    gpio.write(0xFFFF & gpio.direction)
    print("on ", bin(gpio.read()[0]))
    time.sleep(delay)


delay = 1
controller = GpioMpsseController()
try:
    controller.configure(
        "ftdi://ftdi:ft232h/1", frequency=100, direction=0xFFFF, initial=0x0000
    )
    gpio = controller.get_gpio()
    while True:
        toggle(gpio, delay)
finally:
    controller.close()
