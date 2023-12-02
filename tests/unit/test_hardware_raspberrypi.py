import pytest


@pytest.fixture
def rpi_stub(mocker):
    return mocker.MagicMock()


@pytest.fixture
def gpio_mock(rpi_stub):
    return rpi_stub.GPIO


@pytest.fixture
def factory(mocker, rpi_stub, gpio_mock):
    mocker.patch.dict(
        "sys.modules",
        **{
            "RPi": rpi_stub,
            "RPi.GPIO": gpio_mock,
        },
    )
    from autodesk.hardware.raspberrypi import RaspberryPiPinFactory

    factory = RaspberryPiPinFactory()
    yield factory
    factory.close()
    # sys.modules.pop('autodesk.hardware.raspberrypi')


def test_factory_constructor(mocker, rpi_stub, gpio_mock):
    mocker.patch.dict(
        "sys.modules",
        **{
            "RPi": rpi_stub,
            "RPi.GPIO": gpio_mock,
        },
    )
    from autodesk.hardware.raspberrypi import RaspberryPiPinFactory

    RaspberryPiPinFactory()

    gpio_mock.setmode.assert_called_once_with(gpio_mock.BOARD)


def test_factory_close(mocker, rpi_stub, gpio_mock):
    mocker.patch.dict(
        "sys.modules",
        **{
            "RPi": rpi_stub,
            "RPi.GPIO": gpio_mock,
        },
    )
    from autodesk.hardware.raspberrypi import RaspberryPiPinFactory

    factory = RaspberryPiPinFactory()

    factory.close()

    gpio_mock.cleanup.assert_called_once()


def test_factory_create_input(gpio_mock, factory):
    pin_number = 0

    factory.create_input(pin_number)

    gpio_mock.setup.assert_called_once_with(pin_number, gpio_mock.IN)


def test_factory_create_output(gpio_mock, factory):
    pin_number = 0

    factory.create_output(pin_number)

    gpio_mock.setup.assert_called_once_with(pin_number, gpio_mock.OUT)


def test_pin_read_low(gpio_mock, factory):
    pin_number = 0
    gpio_mock.input.return_value = gpio_mock.LOW
    pin = factory.create_input(pin_number)

    actual = pin.read()

    gpio_mock.input.assert_called_once_with(pin_number)
    assert actual == 0


def test_pin_read_high(gpio_mock, factory):
    pin_number = 0
    gpio_mock.input.return_value = gpio_mock.HIGH
    pin = factory.create_input(pin_number)

    actual = pin.read()

    gpio_mock.input.assert_called_once_with(pin_number)
    assert actual == 1


def test_pin_write_low(gpio_mock, factory):
    pin_number = 0
    pin = factory.create_output(pin_number)

    pin.write(0)

    gpio_mock.output.assert_called_once_with(pin_number, gpio_mock.LOW)


def test_pin_write_high(gpio_mock, factory):
    pin_number = 0
    pin = factory.create_output(pin_number)

    pin.write(1)

    gpio_mock.output.assert_called_once_with(pin_number, gpio_mock.HIGH)


def test_pin_write_invalid_value(factory):
    pin_number = 0
    pin = factory.create_output(pin_number)

    with pytest.raises(ValueError):
        pin.write(2)
