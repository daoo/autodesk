from autodesk.model import Down, Up, Active, Inactive
import mock
import pytest


@pytest.fixture
def rpi(mocker):
    return mocker.MagicMock()


@pytest.fixture
def gpio(rpi):
    return rpi.GPIO


@pytest.fixture
def hw(rpi, gpio):
    import sys
    sys.modules['RPi'] = rpi
    sys.modules['RPi.GPIO'] = gpio

    from autodesk.hardware.raspberrypi import RaspberryPi
    yield RaspberryPi(5, (0, 1), 2)
    sys.modules.pop('RPi')
    sys.modules.pop('RPi.GPIO')
    # Must also pop the raspberrypi module as it is cached and contains an
    # reference to the old mocked RPi import.
    sys.modules.pop('autodesk.hardware.raspberrypi')


def test_constructor(mocker, gpio, hw):
    # constructor called by setUp
    gpio.setmode.assert_called_once_with(gpio.BOARD)
    gpio.setup.assert_has_calls([
        mocker.call(0, gpio.OUT),
        mocker.call(1, gpio.OUT),
        mocker.call(2, gpio.OUT)
    ])


def test_close(gpio, hw):
    hw.close()
    gpio.cleanup.assert_called_once()


@mock.patch('time.sleep', autospec=True)
def test_desk_down(sleep, mocker, gpio, hw):
    hw.desk(Down())
    gpio.output.assert_has_calls([
        mocker.call(0, gpio.HIGH),
        mocker.call(0, gpio.LOW)
    ])
    sleep.assert_called_once_with(5)


@mock.patch('time.sleep', autospec=True)
def test_desk_up(sleep, mocker, gpio, hw):
    hw.desk(Up())
    gpio.output.assert_has_calls([
        mocker.call(1, gpio.HIGH),
        mocker.call(1, gpio.LOW)
    ])
    sleep.assert_called_once_with(5)


def test_light_on(gpio, hw):
    hw.light(Active())
    gpio.output.assert_called_once_with(2, gpio.HIGH)


def test_light_off(gpio, hw):
    hw.light(Inactive())
    gpio.output.assert_called_once_with(2, gpio.LOW)
