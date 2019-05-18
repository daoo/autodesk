from autodesk.states import DOWN, UP, ACTIVE, INACTIVE
import pytest


@pytest.fixture
def sleep_mock(mocker):
    return mocker.patch('time.sleep', autospec=True)


@pytest.fixture
def rpi(mocker):
    return mocker.MagicMock()


@pytest.fixture
def gpio_mock(rpi):
    return rpi.GPIO


@pytest.fixture
def hw(rpi, gpio_mock):
    import sys
    sys.modules['RPi'] = rpi
    sys.modules['RPi.GPIO'] = gpio_mock

    from autodesk.hardware.raspberrypi import RaspberryPi
    yield RaspberryPi(5, (0, 1), 2)
    sys.modules.pop('RPi')
    sys.modules.pop('RPi.GPIO')
    # Must also pop the raspberrypi module as it is cached and contains an
    # reference to the old mocked RPi import.
    sys.modules.pop('autodesk.hardware.raspberrypi')


def test_constructor(mocker, gpio_mock, hw):
    # constructor called by hw fixture
    gpio_mock.setmode.assert_called_once_with(gpio_mock.BOARD)
    gpio_mock.setup.assert_has_calls([
        mocker.call(0, gpio_mock.OUT),
        mocker.call(1, gpio_mock.OUT),
        mocker.call(2, gpio_mock.OUT)
    ])


def test_close(gpio_mock, hw):
    hw.close()

    gpio_mock.cleanup.assert_called_once()


def test_desk_down(sleep_mock, mocker, gpio_mock, hw):
    hw.desk(DOWN)

    gpio_mock.output.assert_has_calls([
        mocker.call(0, gpio_mock.HIGH),
        mocker.call(0, gpio_mock.LOW)
    ])
    sleep_mock.assert_called_once_with(5)


def test_desk_up(sleep_mock, mocker, gpio_mock, hw):
    hw.desk(UP)

    gpio_mock.output.assert_has_calls([
        mocker.call(1, gpio_mock.HIGH),
        mocker.call(1, gpio_mock.LOW)
    ])
    sleep_mock.assert_called_once_with(5)


def test_light_on(gpio_mock, hw):
    hw.light(ACTIVE)

    gpio_mock.output.assert_called_once_with(2, gpio_mock.HIGH)


def test_light_off(gpio_mock, hw):
    hw.light(INACTIVE)

    gpio_mock.output.assert_called_once_with(2, gpio_mock.LOW)
