from autodesk.hardware.error import HardwareError
from autodesk.states import DOWN, UP, ACTIVE, INACTIVE
import pytest


@pytest.fixture
def sleep_mock(mocker):
    return mocker.patch('time.sleep', autospec=True)


@pytest.fixture
def gpio(mocker):
    return mocker.MagicMock()


@pytest.fixture
def ft232h(gpio):
    return gpio.FT232H


@pytest.fixture
def device(ft232h):
    return ft232h.FT232H.return_value


@pytest.fixture
def hw(gpio, ft232h):
    import sys
    sys.modules['Adafruit_GPIO'] = gpio
    sys.modules['Adafruit_GPIO.FT232H'] = ft232h

    from autodesk.hardware.ft232h import Ft232h
    yield Ft232h(5, (0, 1), 2)
    sys.modules.pop('Adafruit_GPIO')
    sys.modules.pop('Adafruit_GPIO.FT232H')
    # Must also pop the ft232h module as it is cached and contains an
    # reference to the old mocked RPi import.
    sys.modules.pop('autodesk.hardware.ft232h')


def test_constructor(mocker, gpio, device, hw):
    # constructor called by fixture
    device.setup.assert_has_calls([
        mocker.call(0, gpio.OUT),
        mocker.call(1, gpio.OUT),
        mocker.call(2, gpio.OUT)
    ])


def test_close(device, hw):
    hw.close()

    device.close.assert_called_once()


@pytest.mark.parametrize("state,pin", [(DOWN, 0), (UP, 1)])
def test_desk(mocker, sleep_mock, device, gpio, hw, state, pin):
    hw.desk(state)

    device.output.assert_has_calls([
        mocker.call(pin, gpio.HIGH),
        mocker.call(pin, gpio.LOW)
    ])
    sleep_mock.assert_called_once_with(5)


@pytest.mark.parametrize("state,pin", [(DOWN, 0), (UP, 1)])
def test_desk_failure_recovery(
        mocker, sleep_mock, device, gpio, hw, state, pin):
    def fail_and_reload(a, b):
        device.output.side_effect = None
        raise HardwareError(RuntimeError())
    device.output.side_effect = fail_and_reload

    hw.desk(state)

    device.output.assert_has_calls([
        mocker.call(pin, gpio.HIGH),  # failed attempt
        mocker.call(pin, gpio.HIGH),
        mocker.call(pin, gpio.LOW)
    ])
    sleep_mock.assert_called_once_with(5)


@pytest.mark.parametrize("state,pin", [(DOWN, 0), (UP, 1)])
def test_desk_two_failures_raises(
        mocker, sleep_mock, device, gpio, hw, state, pin):
    device.output.side_effect = HardwareError(RuntimeError())

    with pytest.raises(HardwareError):
        hw.desk(state)

    device.output.assert_has_calls([
        mocker.call(pin, gpio.HIGH),  # failed attempt
        mocker.call(pin, gpio.HIGH),  # failed attempt
    ])
    sleep_mock.assert_not_called()


@pytest.mark.parametrize("state", [INACTIVE, ACTIVE])
def test_light(gpio, device, hw, state):
    hw.light(state)
    device.output.assert_called_once_with(2, state.test(gpio.LOW, gpio.HIGH))


@pytest.mark.parametrize("state", [INACTIVE, ACTIVE])
def test_light_failure_recovery(mocker, gpio, device, hw, state):
    def fail_and_reload(a, b):
        device.output.side_effect = None
        raise HardwareError(RuntimeError())
    device.output.side_effect = fail_and_reload

    hw.light(state)

    device.output.assert_has_calls([
        mocker.call(2, state.test(gpio.LOW, gpio.HIGH)),  # failed attempt
        mocker.call(2, state.test(gpio.LOW, gpio.HIGH)),
    ])


@pytest.mark.parametrize("state", [INACTIVE, ACTIVE])
def test_light_two_failures_raises(mocker, gpio, device, hw, state):
    device.output.side_effect = HardwareError(RuntimeError())

    with pytest.raises(HardwareError):
        hw.light(state)

    device.output.assert_has_calls([
        mocker.call(2, state.test(gpio.LOW, gpio.HIGH)),  # failed attempt
        mocker.call(2, state.test(gpio.LOW, gpio.HIGH)),  # failed attempt
    ])
