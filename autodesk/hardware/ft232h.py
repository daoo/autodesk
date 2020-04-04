from autodesk.hardware.error import HardwareError
from pyftdi.ftdi import FtdiError
from pyftdi.gpio import GpioMpsseController
from pyftdi.usbtools import UsbTools, UsbToolsError
from usb.core import USBError


def set_bit(mask, bit, value):
    if value == 0:
        return mask & ~(1 << bit)
    else:
        return mask | (1 << bit)


class DeviceWrapper:
    def __init__(self):
        self.controller = None
        self.gpio = None
        self.pins = 0

    def _setup(self):
        try:
            self.controller.configure(
                'ftdi://ftdi:ft232h/1',
                frequency=100,
                direction=0xFFFF,
                initial=0x0000,
            )
            self.gpio = self.controller.get_gpio()
            valid_pins = self.gpio.all_pins
            invalid_pins = ((valid_pins | self.pins) & ~valid_pins) & self.pins
            if invalid_pins != 0:
                formatted = \
                    [i for i in range(0, 16) if invalid_pins & 1 << i != 0]
                raise HardwareError(
                    "Cannot use pin(s) {} as GPIO.".format(formatted))
            pin_mask = self.gpio.pins | self.pins
            # A high bit (equal to 1) indicates an output pin.
            new_direction = self.gpio.direction | self.pins
            self.gpio.set_direction(pin_mask, new_direction)
        except UsbToolsError as error:
            self.gpio = None
            raise HardwareError(error)
        except USBError as error:
            self.gpio = None
            raise HardwareError(error)

    def _connect(self):
        if self.gpio:
            return
        if self.controller is not None:
            # Finicky way to get pyftdi to clean up and reconnect properly
            # after a hardware disconnect. Not necessary on first connect.
            UsbTools.release_device(self.controller._ftdi._usb_dev)
            self.controller.close()
            UsbTools.flush_cache()
        else:
            self.controller = GpioMpsseController()
        self._setup()

    def disconnect(self):
        if self.gpio:
            self.gpio = None
            self.controller.close()

    def add_pin(self, pin):
        self.pins = self.pins | 1 << pin

    def _write_no_error_handling(self, pin, value):
        current = self.gpio.read()[0]
        new = set_bit(current, pin, value)
        self.gpio.write(new & self.gpio.direction)

    def write(self, pin, value):
        self._connect()
        try:
            self._write_no_error_handling(pin, value)
        except FtdiError as error1:
            try:
                self.disconnect()
                self._connect()
                self._write_no_error_handling(pin, value)
            except FtdiError:
                raise HardwareError(error1)


class Ft232hOutputPin:
    def __init__(self, wrapper, pin):
        self.wrapper = wrapper
        self.pin = pin

    def write(self, value):
        if value != 0 and value != 1:
            raise ValueError(
                'Pin value must be 0 or 1 but got {0}'.format(value))
        self.wrapper.write(self.pin, value)


class Ft232hPinFactory:
    def __enter__(self):
        self.wrapper = DeviceWrapper()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wrapper.disconnect()

    def create(self, pin):
        self.wrapper.add_pin(pin)
        return Ft232hOutputPin(self.wrapper, pin)
