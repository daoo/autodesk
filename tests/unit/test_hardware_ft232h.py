from autodesk.hardware.error import HardwareError
from autodesk.hardware.ft232h import Ft232hPinFactory
from pyftdi.ftdi import FtdiError
from pyftdi.usbtools import UsbToolsError
from usb.core import USBError
import pytest


@pytest.fixture
def controller_fake(mocker):
    return mocker \
        .patch('autodesk.hardware.ft232h.GpioMpsseController') \
        .return_value


@pytest.fixture
def gpio_fake(controller_fake):
    return controller_fake.get_gpio.return_value


@pytest.fixture
def factory(controller_fake, gpio_fake):
    with Ft232hPinFactory() as factory_instance:
        yield factory_instance


def test_factory_enter(controller_fake):
    with Ft232hPinFactory():
        pass


def test_factory_exit(controller_fake, gpio_fake):
    pin_number = 1
    gpio_fake.all_pins = 0b0110

    with Ft232hPinFactory() as factory:
        pin = factory.create(pin_number)
        pin.write(0)  # Must do a write to trigger connection

    controller_fake.close.assert_called_once()


def test_factory_create_followed_by_write(gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.pins = 0b0100
    gpio_fake.direction = 0b0100

    pin = factory.create(pin_number)
    pin.write(0)  # Must do a write to trigger connection

    expected_pin_mask = 0b0110
    expected_direction = 0b0110
    gpio_fake.set_direction.assert_called_once_with(
        expected_pin_mask, expected_direction)


def test_factory_create_invalid_pin(gpio_fake, factory):
    pin_number = 0
    gpio_fake.all_pins = 0b0110

    with pytest.raises(HardwareError):
        pin = factory.create(pin_number)
        pin.write(0)  # Must do a write to trigger connection


def test_pin_write_low(gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.pins = 0b0110
    gpio_fake.direction = 0b0110
    gpio_fake.read.return_value = (0b0110,)
    pin = factory.create(pin_number)

    pin.write(0)

    gpio_fake.write.assert_called_once_with(0b0100)


def test_pin_write_high(gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.pins = 0b0110
    gpio_fake.direction = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create(pin_number)

    pin.write(1)

    gpio_fake.write.assert_called_once_with(0b0110)


def test_pin_write_invalid_value(factory):
    pin_number = 0
    pin = factory.create(pin_number)

    with pytest.raises(ValueError):
        pin.write(2)


def test_pin_write_failure_recovery(mocker, gpio_fake, factory):
    def fail_once(value):
        gpio_fake.write.side_effect = None
        raise FtdiError('Stubbed error for unit testing.')
    gpio_fake.write.side_effect = fail_once
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.pins = 0b0110
    gpio_fake.direction = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create(pin_number)

    pin.write(1)

    gpio_fake.write.assert_has_calls([
        mocker.call(0b0110),  # failed attempt
        mocker.call(0b0110),
    ])


def test_pin_write_two_failures_raises(mocker, gpio_fake, factory):
    gpio_fake.write.side_effect = FtdiError(
        'Stubbed error for unit testing.')
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.pins = 0b0110
    gpio_fake.direction = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create(pin_number)

    with pytest.raises(HardwareError):
        pin.write(1)

    gpio_fake.write.assert_has_calls([
        mocker.call(0b0110),  # failed attempt
        mocker.call(0b0110),  # failed attempt
    ])


def test_two_writes_connects_once(controller_fake, gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.pins = 0b0110
    gpio_fake.direction = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create(pin_number)

    pin.write(0)
    pin.write(1)

    controller_fake.configure.assert_called_once()


def test_connect_usb_tools_error_raises(controller_fake, gpio_fake, factory):
    controller_fake.configure.side_effect = UsbToolsError(
        'Stubbed error for unit testing.')
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.pins = 0b0110
    gpio_fake.direction = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create(pin_number)

    with pytest.raises(HardwareError):
        pin.write(1)  # Must do a write to trigger connection


def test_connect_usb_error_raises(controller_fake, gpio_fake, factory):
    controller_fake.configure.side_effect = USBError(
        'Stubbed error for unit testing.')
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.pins = 0b0110
    gpio_fake.direction = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create(pin_number)

    with pytest.raises(HardwareError):
        pin.write(1)  # Must do a write to trigger connection
