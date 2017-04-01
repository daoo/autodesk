from unittest.mock import MagicMock, call
mock = MagicMock()
mock.rpi = MagicMock()
mock.time = MagicMock()

import sys
sys.modules['RPi'] = mock.rpi
sys.modules['RPi.GPIO'] = mock.rpi.GPIO
sys.modules['time'] = mock.time

from autodesk.hardware import Hardware
from autodesk.model import Down, Up


def test_hardware_setup():
    mock.reset_mock()
    hw = Hardware(5, (0, 1))
    hw.setup()
    assert mock.rpi.GPIO.setmode.call_args[0] == ((mock.rpi.GPIO.BOARD),)
    assert mock.rpi.GPIO.setup.call_args_list == [
        ((0, mock.rpi.GPIO.OUT),),
        ((1, mock.rpi.GPIO.OUT),)
    ]
    assert not mock.rpi.GPIO.cleanup.called


def test_hardware_cleanup():
    mock.reset_mock()
    hw = Hardware(5, (0, 1))
    hw.cleanup()
    assert not mock.rpi.GPIO.setmode.called
    assert mock.rpi.GPIO.cleanup.called


def test_hardware_go_down():
    mock.reset_mock()
    hw = Hardware(5, (0, 1))
    hw.go(Down())
    assert mock.mock_calls == [
        call.rpi.GPIO.output(0, mock.rpi.GPIO.HIGH),
        call.time.sleep(5),
        call.rpi.GPIO.output(0, mock.rpi.GPIO.LOW),
    ]


def test_hardware_go_up():
    mock.reset_mock()
    hw = Hardware(5, (0, 1))
    hw.go(Up())
    assert mock.mock_calls == [
        call.rpi.GPIO.output(1, mock.rpi.GPIO.HIGH),
        call.time.sleep(5),
        call.rpi.GPIO.output(1, mock.rpi.GPIO.LOW),
    ]
