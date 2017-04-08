import unittest
from unittest.mock import MagicMock, call
from autodesk.model import Down, Up

mock = MagicMock()
mock.rpi = MagicMock()
mock.time = MagicMock()

import sys
sys.modules['RPi'] = mock.rpi
sys.modules['RPi.GPIO'] = mock.rpi.GPIO
sys.modules['time'] = mock.time

from autodesk.hardware import Hardware

class TestHardware(unittest.TestCase):
    def setUp(self):
        mock.reset_mock()
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
        self.assertEqual(mock.mock_calls, [
            call.rpi.GPIO.output(0, mock.rpi.GPIO.HIGH),
            call.time.sleep(5),
            call.rpi.GPIO.output(0, mock.rpi.GPIO.LOW),
        ])

    def test_hardware_go_up(self):
        self.hardware.go(Up())
        self.assertEqual(mock.mock_calls, [
            call.rpi.GPIO.output(1, mock.rpi.GPIO.HIGH),
            call.time.sleep(5),
            call.rpi.GPIO.output(1, mock.rpi.GPIO.LOW),
        ])
