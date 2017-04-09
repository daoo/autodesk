import unittest
from unittest.mock import MagicMock, call, patch
from autodesk.model import Down, Up


class TestHardware(unittest.TestCase):
    def setUp(self):
        self.time_patcher = patch('time.sleep')
        self.time_sleep = self.time_patcher.start()
        self.addCleanup(self.time_patcher.stop)

        self.rpi = MagicMock()
        self.gpio = self.rpi.GPIO
        import sys
        sys.modules['RPi'] = self.rpi
        self.addCleanup(sys.modules.pop, 'RPi')
        sys.modules['RPi.GPIO'] = self.gpio
        self.addCleanup(sys.modules.pop, 'RPi.GPIO')

        from autodesk.hardware import Hardware
        # The hardware module must also be removed since it is cached and
        # maintains a reference to the mock RPi module.
        self.addCleanup(sys.modules.pop, 'autodesk.hardware')
        self.hardware = Hardware(5, (0, 1))

    def test_hardware_setup(self):
        self.hardware.setup()
        self.gpio.setmode.assert_called_with(self.gpio.BOARD)
        self.gpio.setup.assert_has_calls([
            call(0, self.gpio.OUT),
            call(1, self.gpio.OUT)
        ])
        self.gpio.cleanup.assert_not_called()

    def test_hardware_cleanup(self):
        self.hardware.cleanup()
        self.gpio.cleanup.assert_called_once()
        self.gpio.setmode.assert_not_called()

    def test_hardware_go_down(self):
        self.hardware.go(Down())
        self.gpio.output.assert_has_calls([
            call(0, self.gpio.HIGH),
            call(0, self.gpio.LOW)
        ])
        self.time_sleep.assert_called_once_with(5)

    def test_hardware_go_up(self):
        self.hardware.go(Up())
        self.gpio.output.assert_has_calls([
            call(1, self.gpio.HIGH),
            call(1, self.gpio.LOW)
        ])
        self.time_sleep.assert_called_once_with(5)
