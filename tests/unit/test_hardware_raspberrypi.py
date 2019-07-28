import pytest


@pytest.fixture
def rpi_stub(mocker):
    return mocker.MagicMock()


@pytest.fixture
def gpio_mock(rpi_stub):
    return rpi_stub.GPIO


class RaspberryPiPinFactoryWithMockedGPIO:
    def __init__(self, rpi_stub, gpio_fake):
        self.rpi_stub = rpi_stub
        self.gpio_fake = gpio_fake

    def __enter__(self):
        import sys
        sys.modules['RPi'] = self.rpi_stub
        sys.modules['RPi.GPIO'] = self.gpio_fake

        from autodesk.hardware.raspberrypi import RaspberryPiPinFactory
        self.factory = RaspberryPiPinFactory()
        self.factory.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.factory.__exit__(exc_type, exc_val, exc_tb)
        import sys
        sys.modules.pop('RPi')
        sys.modules.pop('RPi.GPIO')
        # Must also pop the raspberrypi module as it is cached and contains an
        # reference to the old mocked RPi import.
        sys.modules.pop('autodesk.hardware.raspberrypi')


@pytest.fixture
def factory(rpi_stub, gpio_mock):
    with RaspberryPiPinFactoryWithMockedGPIO(rpi_stub, gpio_mock) as wrapper:
        yield wrapper.factory


def test_factory_enter(rpi_stub, gpio_mock):
    with RaspberryPiPinFactoryWithMockedGPIO(rpi_stub, gpio_mock):
        gpio_mock.setmode.assert_called_once_with(gpio_mock.BOARD)


def test_factory_exit(rpi_stub, gpio_mock):
    with RaspberryPiPinFactoryWithMockedGPIO(rpi_stub, gpio_mock):
        pass
    gpio_mock.cleanup.assert_called_once()


def test_factory_create(gpio_mock, factory):
    pin_number = 0

    factory.create(pin_number)

    gpio_mock.setup.assert_called_once_with(pin_number, gpio_mock.OUT)


def test_pin_write_low(gpio_mock, factory):
    pin_number = 0
    pin = factory.create(pin_number)

    pin.write(0)

    gpio_mock.output.assert_called_once_with(pin_number, gpio_mock.LOW)


def test_pin_write_high(gpio_mock, factory):
    pin_number = 0
    pin = factory.create(pin_number)

    pin.write(1)

    gpio_mock.output.assert_called_once_with(pin_number, gpio_mock.HIGH)


def test_pin_write_invalid_value(factory):
    pin_number = 0
    pin = factory.create(pin_number)

    with pytest.raises(ValueError):
        pin.write(2)
