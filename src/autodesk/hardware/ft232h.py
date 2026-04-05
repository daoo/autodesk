from collections.abc import Callable
from typing import Any, Protocol, TypeVar, cast

from pyftdi.ftdi import FtdiError
from pyftdi.gpio import GpioMpsseController
from pyftdi.usbtools import UsbTools, UsbToolsError
from usb.core import USBError

from autodesk.hardware.error import HardwareError
from autodesk.hardware.types import (
    InputPin,
    OutputPin,
    PinFactory,
    PinValue,
    validate_pin_value,
)


class _GpioPort(Protocol):
    all_pins: int
    direction: int

    def read(self) -> tuple[int, ...]: ...

    def write(self, value: int) -> None: ...

    def set_direction(self, pins: int, direction: int) -> None: ...


T = TypeVar("T")


def set_bit(mask: int, bit: int, value: PinValue) -> int:
    if value == 0:
        return mask & ~(1 << bit)
    return mask | (1 << bit)


class DeviceWrapper:
    def __init__(self):
        self.controller: GpioMpsseController | None = None
        self.gpio: _GpioPort | None = None
        self.output_pins = 0
        self.input_pins = 0

    def _setup(self) -> None:
        if self.controller is None:
            raise RuntimeError("FT232H controller is not initialized")
        try:
            self.controller.configure(
                "ftdi://ftdi:ft232h/1",
                frequency=100,
                direction=0xFFFF,
                initial=0x0000,
            )
            self.gpio = cast(_GpioPort, self.controller.get_gpio())
            valid_pins = self.gpio.all_pins
            used_pins = self.output_pins | self.input_pins
            invalid_pins = used_pins & ~valid_pins
            if invalid_pins != 0:
                formatted = [i for i in range(0, 16) if invalid_pins & 1 << i != 0]
                raise HardwareError(f"Cannot use pin(s) {formatted} as GPIO.")
            # A low bit (equal to 0) indicates an input pin.
            # A high bit (equal to 1) indicates an output pin.
            new_direction = self.output_pins & ~self.input_pins
            self.gpio.set_direction(used_pins, new_direction)
        except UsbToolsError as error:
            self.gpio = None
            raise HardwareError(error) from None
        except USBError as error:
            self.gpio = None
            raise HardwareError(error) from None

    def _release_controller_device(self) -> None:
        if self.controller is None:
            return
        ftdi = getattr(self.controller, "_ftdi", None)
        usb_dev = getattr(ftdi, "_usb_dev", None)
        if usb_dev is not None:
            UsbTools.release_device(cast(Any, usb_dev))

    def _connect(self) -> None:
        if self.gpio is not None:
            return
        if self.controller is not None:
            # Finicky way to get pyftdi to clean up and reconnect properly
            # after a hardware disconnect. Not necessary on first connect.
            self._release_controller_device()
            self.controller.close()
            UsbTools.flush_cache()
        else:
            self.controller = GpioMpsseController()
        self._setup()

    def disconnect(self) -> None:
        self.gpio = None
        if self.controller is not None:
            self.controller.close()

    def add_output(self, pin: int) -> None:
        self.output_pins = self.output_pins | 1 << pin

    def add_input(self, pin: int) -> None:
        self.input_pins = self.input_pins | 1 << pin

    def _require_gpio(self) -> _GpioPort:
        if self.gpio is None:
            raise RuntimeError("FT232H GPIO is not connected")
        return self.gpio

    def _read_no_error_handling(self, pin: int) -> PinValue:
        gpio = self._require_gpio()
        current = gpio.read()[0]
        return cast(PinValue, (current >> pin) & 1)

    def _write_no_error_handling(self, pin: int, value: PinValue) -> None:
        gpio = self._require_gpio()
        current = gpio.read()[0]
        new = set_bit(current, pin, value)
        gpio.write(new & gpio.direction)

    def _reconnect_and_try_again(self, action: Callable[[], T]) -> T:
        self._connect()
        try:
            return action()
        except FtdiError as error1:
            try:
                self.disconnect()
                self._connect()
                return action()
            except FtdiError as err:
                raise HardwareError(error1) from err

    def read(self, pin: int) -> PinValue:
        return self._reconnect_and_try_again(lambda: self._read_no_error_handling(pin))

    def write(self, pin: int, value: PinValue) -> None:
        self._reconnect_and_try_again(lambda: self._write_no_error_handling(pin, value))


class Ft232hOutputPin(OutputPin):
    def __init__(self, wrapper: DeviceWrapper, pin: int):
        self.wrapper = wrapper
        self.pin = pin

    def write(self, value: int) -> None:
        self.wrapper.write(self.pin, validate_pin_value(value))


class Ft232hInputPin(InputPin):
    def __init__(self, wrapper: DeviceWrapper, pin: int):
        self.wrapper = wrapper
        self.pin = pin

    def read(self) -> PinValue:
        return self.wrapper.read(self.pin)


class Ft232hPinFactory(PinFactory):
    def __init__(self):
        self.wrapper = DeviceWrapper()

    def close(self) -> None:
        self.wrapper.disconnect()

    def create_input(self, pin: int) -> Ft232hInputPin:
        self.wrapper.add_input(pin)
        return Ft232hInputPin(self.wrapper, pin)

    def create_output(self, pin: int) -> Ft232hOutputPin:
        self.wrapper.add_output(pin)
        return Ft232hOutputPin(self.wrapper, pin)
