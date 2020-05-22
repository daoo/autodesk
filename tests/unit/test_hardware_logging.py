from autodesk.hardware.logging import LoggingPinFactory
import pytest


@pytest.fixture
def mock_pin(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_factory(mocker, mock_pin):
    factory = mocker.MagicMock()
    factory.create.return_value = mock_pin
    return factory


@pytest.fixture
def factory(mock_factory):
    with LoggingPinFactory(mock_factory) as pin_factory:
        yield pin_factory


def test_factory_enter(mock_factory):
    with LoggingPinFactory(mock_factory):
        mock_factory.__enter__.assert_called_once()


def test_factory_exit(mock_factory):
    with LoggingPinFactory(mock_factory):
        pass
    mock_factory.__exit__.assert_called_once()


def test_factory_create(mock_factory, factory):
    pin_number = 0

    factory.create(pin_number)

    mock_factory.create.assert_called_once_with(pin_number)


def test_pin_write_low(mock_pin, factory):
    pin_number = 0
    pin = factory.create(pin_number)

    pin.write(0)

    mock_pin.write.assert_called_once_with(0)


def test_pin_write_high(mock_pin, factory):
    pin_number = 0
    pin = factory.create(pin_number)

    pin.write(1)

    mock_pin.write.assert_called_once_with(1)
