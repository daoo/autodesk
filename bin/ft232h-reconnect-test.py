#!/usr/bin/env python
from pyftdi.gpio import GpioMpsseController
import traceback
from pyftdi.usbtools import UsbTools

print("Creating, configuring, writing and closing a GpioMpsseController...")
controller = GpioMpsseController()
controller.configure(
    "ftdi://ftdi:ft232h/1", frequency=100, direction=0xFFFF, initial=0x0000
)
gpio = controller.get_gpio()
gpio.write(0xFFFF & gpio.direction)
value = gpio.read()[0]
print("  Success (read {0})!".format(hex(value)))

input("Now, disconnect and reconnect hardware and press enter.")
try:
    UsbTools.release_device(controller._ftdi._usb_dev)
    controller.close()
    UsbTools.flush_cache()
    controller.configure(
        "ftdi://ftdi:ft232h/1", frequency=100, direction=0xFFFF, initial=0x0000
    )
    gpio = controller.get_gpio()
    gpio.write(0xFFFF & gpio.direction)
    print("  Success!")
except Exception:
    print(traceback.format_exc())
