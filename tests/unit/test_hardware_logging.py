import pytest

from autodesk.hardware.logging import LoggingPinFactory


@pytest.fixture
def mock_pin(mocker):
    return mocker.patch("autodesk.hardware.noop.NoopPin")


@pytest.fixture
def mock_factory(mocker, mock_pin):
    factory = mocker.patch("autodesk.hardware.noop.NoopPinFactory", autospec=True)
    factory.create_output.return_value = mock_pin
    factory.create_input.return_value = mock_pin
    return factory


@pytest.fixture
def factory(mock_factory):
    pin_factory = LoggingPinFactory(mock_factory)
    yield pin_factory
    pin_factory.close()


def test_factory_close(mock_factory):
    pin_factory = LoggingPinFactory(mock_factory)

    pin_factory.close()

    mock_factory.close.assert_called_once()


def test_factory_create_input(mock_factory, factory):
    pin_number = 0

    factory.create_input(pin_number)

    mock_factory.create_input.assert_called_once_with(pin_number)


def test_factory_create_output(mock_factory, factory):
    pin_number = 0

    factory.create_output(pin_number)

    mock_factory.create_output.assert_called_once_with(pin_number)


@pytest.mark.parametrize("value", [0, 1])
def test_pin_read_return_same_as_mock(mock_pin, factory, value):
    pin_number = 0
    mock_pin.read.return_value = value
    pin = factory.create_input(pin_number)

    actual = pin.read()

    assert actual == value


def test_pin_write_low(mock_pin, factory):
    pin_number = 0
    pin = factory.create_output(pin_number)

    pin.write(0)

    mock_pin.write.assert_called_once_with(0)


def test_pin_write_high(mock_pin, factory):
    pin_number = 0
    pin = factory.create_output(pin_number)

    pin.write(1)

    mock_pin.write.assert_called_once_with(1)
