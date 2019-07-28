from autodesk.hardware.error import HardwareError
import pytest


@pytest.fixture
def gpio_stub(mocker):
    return mocker.MagicMock()


@pytest.fixture
def ft232h_stub(gpio_stub):
    return gpio_stub.FT232H


@pytest.fixture
def device_mock(ft232h_stub):
    return ft232h_stub.FT232H.return_value


class Ft232hPinFactoryWithMockedGPIO:
    def __init__(self, gpio_stub, ft232h_stub):
        self.gpio_stub = gpio_stub
        self.ft232h_stub = ft232h_stub

    def __enter__(self):
        import sys
        sys.modules['Adafruit_GPIO'] = self.gpio_stub
        sys.modules['Adafruit_GPIO.FT232H'] = self.ft232h_stub

        from autodesk.hardware.ft232h import Ft232hPinFactory
        self.factory = Ft232hPinFactory()
        self.factory.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.factory.__exit__(exc_type, exc_val, exc_tb)
        import sys
        sys.modules.pop('Adafruit_GPIO')
        sys.modules.pop('Adafruit_GPIO.FT232H')
        # Must also pop the ft232h module as it is cached and contains an
        # reference to the old mocked RPi import.
        sys.modules.pop('autodesk.hardware.ft232h')


@pytest.fixture
def factory(gpio_stub, ft232h_stub):
    with Ft232hPinFactoryWithMockedGPIO(gpio_stub, ft232h_stub) as wrapper:
        yield wrapper.factory


def test_factory_enter(gpio_stub, ft232h_stub, device_mock):
    with Ft232hPinFactoryWithMockedGPIO(gpio_stub, ft232h_stub):
        pass


def test_factory_exit(gpio_stub, ft232h_stub, device_mock):
    with Ft232hPinFactoryWithMockedGPIO(gpio_stub, ft232h_stub):
        pass
    device_mock.close.assert_called_once()


def test_factory_create(gpio_stub, device_mock, factory):
    pin_number = 0

    factory.create(pin_number)

    device_mock.setup.assert_called_once_with(pin_number, gpio_stub.OUT)


def test_pin_write_low(device_mock, gpio_stub, factory):
    pin_number = 0
    pin = factory.create(pin_number)

    pin.write(0)

    device_mock.output.assert_called_once_with(pin_number, gpio_stub.LOW)


def test_pin_write_high(device_mock, gpio_stub, factory):
    pin_number = 0
    pin = factory.create(pin_number)

    pin.write(1)

    device_mock.output.assert_called_once_with(pin_number, gpio_stub.HIGH)


def test_pin_write_invalid_value(factory):
    pin_number = 0
    pin = factory.create(pin_number)

    with pytest.raises(ValueError):
        pin.write(2)


def test_pin_write_failure_recovery(mocker, device_mock, gpio_stub, factory):
    def fail_and_reload(a, b):
        device_mock.output.side_effect = None
        raise RuntimeError()
    device_mock.output.side_effect = fail_and_reload
    pin_number = 0
    pin = factory.create(pin_number)

    pin.write(0)

    device_mock.output.assert_has_calls([
        mocker.call(pin_number, gpio_stub.LOW),  # failed attempt
        mocker.call(pin_number, gpio_stub.LOW),
    ])


def test_pin_write_two_failures_raises(
        mocker, device_mock, gpio_stub, factory):
    pin_number = 0
    pin = factory.create(pin_number)
    device_mock.output.side_effect = RuntimeError()

    with pytest.raises(HardwareError):
        pin.write(0)

    device_mock.output.assert_has_calls([
        mocker.call(pin_number, gpio_stub.LOW),  # failed attempt
        mocker.call(pin_number, gpio_stub.LOW),  # failed attempt
    ])
