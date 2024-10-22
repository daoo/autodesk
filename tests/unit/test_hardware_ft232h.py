import pytest
from pyftdi.ftdi import FtdiError
from pyftdi.usbtools import UsbToolsError
from usb.core import USBError

from autodesk.hardware.error import HardwareError
from autodesk.hardware.ft232h import Ft232hPinFactory


@pytest.fixture
def controller_fake(mocker):
    return mocker.patch("autodesk.hardware.ft232h.GpioMpsseController").return_value


@pytest.fixture
def gpio_fake(controller_fake):
    fake = controller_fake.get_gpio.return_value

    def assign_direction(_, direction):
        fake.direction = direction

    fake.set_direction.side_effect = assign_direction
    return fake


@pytest.fixture
def factory():
    factory_instance = Ft232hPinFactory()
    yield factory_instance
    factory_instance.close()


def test_factory_constructor():
    factory = Ft232hPinFactory()
    factory.close()


def test_factory_close(controller_fake, gpio_fake):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    factory = Ft232hPinFactory()
    pin = factory.create_output(pin_number)
    pin.write(0)  # Must do a write to trigger connection

    factory.close()

    controller_fake.close.assert_called_once()


def test_factory_create_input_followed_by_read(gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110

    pin = factory.create_input(pin_number)
    pin.read()  # Must do a write to trigger connection

    expected_pin_mask = 0b0010
    expected_direction = 0b0000
    gpio_fake.set_direction.assert_called_once_with(
        expected_pin_mask, expected_direction
    )


def test_factory_create_output_followed_by_write(gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110

    pin = factory.create_output(pin_number)
    pin.write(0)  # Must do a write to trigger connection

    expected_pin_mask = 0b0010
    expected_direction = 0b0010
    gpio_fake.set_direction.assert_called_once_with(
        expected_pin_mask, expected_direction
    )


def test_factory_create_input_invalid_pin(gpio_fake, factory):
    pin_number = 0
    gpio_fake.all_pins = 0b0110

    with pytest.raises(HardwareError):
        pin = factory.create_input(pin_number)
        pin.read()  # Must do a write to trigger connection


def test_factory_create_output_invalid_pin(gpio_fake, factory):
    pin_number = 0
    gpio_fake.all_pins = 0b0110

    with pytest.raises(HardwareError):
        pin = factory.create_output(pin_number)
        pin.write(0)  # Must do a write to trigger connection


def test_pin_read_low(gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_input(pin_number)

    actual = pin.read()

    assert actual == 0


def test_pin_read_high(gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0110,)
    pin = factory.create_input(pin_number)

    actual = pin.read()

    assert actual == 1


def test_pin_write_low(gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0110,)
    pin = factory.create_output(pin_number)

    pin.write(0)

    gpio_fake.write.assert_called_once_with(0b0000)


def test_pin_write_high(gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_output(pin_number)

    pin.write(1)

    gpio_fake.write.assert_called_once_with(0b0010)


def test_pin_write_invalid_value(factory):
    pin_number = 0
    pin = factory.create_output(pin_number)

    with pytest.raises(ValueError):
        pin.write(2)


def test_pin_read_failure_recovery(mocker, gpio_fake, factory):
    def fail_once():
        gpio_fake.read.side_effect = None
        raise FtdiError("Stubbed error for unit testing.")

    gpio_fake.read.side_effect = fail_once
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_input(pin_number)

    actual = pin.read()

    gpio_fake.read.assert_has_calls(
        [
            mocker.call(),  # failed attempt
            mocker.call(),
        ]
    )
    assert actual == 0


def test_pin_read_two_failures_raises(mocker, gpio_fake, factory):
    gpio_fake.read.side_effect = FtdiError("Stubbed error for unit testing.")
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_input(pin_number)

    with pytest.raises(HardwareError):
        pin.read()

    gpio_fake.read.assert_has_calls(
        [
            mocker.call(),  # failed attempt
            mocker.call(),  # failed attempt
        ]
    )


def test_pin_write_failure_recovery(mocker, gpio_fake, factory):
    def fail_once(_):
        gpio_fake.write.side_effect = None
        raise FtdiError("Stubbed error for unit testing.")

    gpio_fake.write.side_effect = fail_once
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_output(pin_number)

    pin.write(1)

    gpio_fake.write.assert_has_calls(
        [
            mocker.call(0b0010),  # failed attempt
            mocker.call(0b0010),
        ]
    )


def test_pin_write_two_failures_raises(mocker, gpio_fake, factory):
    gpio_fake.write.side_effect = FtdiError("Stubbed error for unit testing.")
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_output(pin_number)

    with pytest.raises(HardwareError):
        pin.write(1)

    gpio_fake.write.assert_has_calls(
        [
            mocker.call(0b0010),  # failed attempt
            mocker.call(0b0010),  # failed attempt
        ]
    )


def test_two_reads_connects_once(controller_fake, gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_input(pin_number)

    pin.read()
    pin.read()

    controller_fake.configure.assert_called_once()


def test_two_writes_connects_once(controller_fake, gpio_fake, factory):
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_output(pin_number)

    pin.write(0)
    pin.write(1)

    controller_fake.configure.assert_called_once()


def test_input_connect_usb_tools_error(controller_fake, gpio_fake, factory):
    controller_fake.configure.side_effect = UsbToolsError(
        "Stubbed error for unit testing."
    )
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_input(pin_number)

    with pytest.raises(HardwareError):
        pin.read()  # Must do a read to trigger connection


def test_input_connect_usb_error(controller_fake, gpio_fake, factory):
    controller_fake.configure.side_effect = USBError("Stubbed error for unit testing.")
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_input(pin_number)

    with pytest.raises(HardwareError):
        pin.read()  # Must do a read to trigger connection


def test_output_connect_usb_tools_error(controller_fake, gpio_fake, factory):
    controller_fake.configure.side_effect = UsbToolsError(
        "Stubbed error for unit testing."
    )
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_output(pin_number)

    with pytest.raises(HardwareError):
        pin.write(1)  # Must do a write to trigger connection


def test_output_connect_usb_error(controller_fake, gpio_fake, factory):
    controller_fake.configure.side_effect = USBError("Stubbed error for unit testing.")
    pin_number = 1
    gpio_fake.all_pins = 0b0110
    gpio_fake.read.return_value = (0b0100,)
    pin = factory.create_output(pin_number)

    with pytest.raises(HardwareError):
        pin.write(1)  # Must do a write to trigger connection
