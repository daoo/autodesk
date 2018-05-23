from autodesk.model import Down, Up, Active, Inactive
import mock
import pytest


@pytest.fixture
def gpio():
    return mock.MagicMock()


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


def test_constructor(gpio, ft232h, device, hw):
    # constructor called by fixture
    device.setup.assert_has_calls([
        mock.call(0, gpio.OUT),
        mock.call(1, gpio.OUT),
        mock.call(2, gpio.OUT)
    ])


def test_close(device, hw):
    hw.close()
    device.close.assert_called_once()


@mock.patch('time.sleep')
@pytest.mark.parametrize("state,pin", [(Down(), 0), (Up(), 1)])
def test_desk(sleep, device, gpio, hw, state, pin):
    hw.desk(state)
    device.output.assert_has_calls([
        mock.call(pin, gpio.HIGH),
        mock.call(pin, gpio.LOW)
    ])
    sleep.assert_called_once_with(5)


@mock.patch('time.sleep')
@pytest.mark.parametrize("state,pin", [(Down(), 0), (Up(), 1)])
def test_desk_failure_recovery(sleep, device, gpio, hw, state, pin):
    def fail_and_reload(a, b):
        device.output.side_effect = None
        raise RuntimeError
    device.output.side_effect = fail_and_reload

    hw.desk(state)

    device.output.assert_has_calls([
        mock.call(pin, gpio.HIGH),  # failed attempt
        mock.call(pin, gpio.HIGH),
        mock.call(pin, gpio.LOW)
    ])
    sleep.assert_called_once_with(5)


@mock.patch('time.sleep')
@pytest.mark.parametrize("state,pin", [(Down(), 0), (Up(), 1)])
def test_desk_two_failures_raises(sleep, device, gpio, hw, state, pin):
    device.output.side_effect = RuntimeError

    with pytest.raises(RuntimeError):
        hw.desk(state)

    device.output.assert_has_calls([
        mock.call(pin, gpio.HIGH),  # failed attempt
        mock.call(pin, gpio.HIGH),  # failed attempt
    ])
    sleep.assert_not_called()


@pytest.mark.parametrize("state", [Inactive(), Active()])
def test_light(gpio, device, hw, state):
    hw.light(state)
    device.output.assert_called_once_with(2, state.test(gpio.LOW, gpio.HIGH))


@pytest.mark.parametrize("state", [Inactive(), Active()])
def test_light_failure_recovery(gpio, device, hw, state):
    def fail_and_reload(a, b):
        device.output.side_effect = None
        raise RuntimeError
    device.output.side_effect = fail_and_reload

    hw.light(state)

    device.output.assert_has_calls([
        mock.call(2, state.test(gpio.LOW, gpio.HIGH)),  # failed attempt
        mock.call(2, state.test(gpio.LOW, gpio.HIGH)),
    ])


@pytest.mark.parametrize("state", [Inactive(), Active()])
def test_light_two_failures_raises(gpio, device, hw, state):
    device.output.side_effect = RuntimeError

    with pytest.raises(RuntimeError):
        hw.light(state)

    device.output.assert_has_calls([
        mock.call(2, state.test(gpio.LOW, gpio.HIGH)),  # failed attempt
        mock.call(2, state.test(gpio.LOW, gpio.HIGH)),  # failed attempt
    ])
