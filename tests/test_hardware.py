import unittest
from unittest.mock import MagicMock, call, patch
from autodesk.model import Down, Up

mock = MagicMock()
mock.rpi = MagicMock()

import sys
sys.modules['RPi'] = mock.rpi
sys.modules['RPi.GPIO'] = mock.rpi.GPIO

from autodesk.hardware import Hardware

class TestHardware(unittest.TestCase):
    def setUp(self):
        mock.reset_mock()

        self.time_patcher = patch('time.sleep')
        self.time_sleep = self.time_patcher.start()
        self.addCleanup(self.time_patcher.stop)

        self.hardware = Hardware(5, (0, 1))

    def test_hardware_setup(self):
        self.hardware.setup()
        mock.rpi.GPIO.setmode.assert_called_with(mock.rpi.GPIO.BOARD)
        expected = [
            call(0, mock.rpi.GPIO.OUT),
            call(1, mock.rpi.GPIO.OUT)
        ]
        self.assertEqual(mock.rpi.GPIO.setup.call_args_list, expected)
        self.assertFalse(mock.rpi.GPIO.cleanup.called)

    def test_hardware_cleanup(self):
        self.hardware.cleanup()
        mock.rpi.GPIO.cleanup.assert_called_once()
        mock.rpi.GPIO.setmode.assert_not_called()

    def test_hardware_go_down(self):
        self.hardware.go(Down())
        expected = [call(0, mock.rpi.GPIO.HIGH), call(0, mock.rpi.GPIO.LOW)]
        self.assertEqual(mock.rpi.GPIO.output.call_args_list, expected)
        self.time_sleep.assert_called_once_with(5)

    def test_hardware_go_up(self):
        self.hardware.go(Up())
        expected = [call(1, mock.rpi.GPIO.HIGH), call(1, mock.rpi.GPIO.LOW)]
        self.assertEqual(mock.rpi.GPIO.output.call_args_list, expected)
        self.time_sleep.assert_called_once_with(5)
