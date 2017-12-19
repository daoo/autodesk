from autodesk.hardware import Hardware
from autodesk.model import Down, Up, Active, Inactive
from unittest.mock import MagicMock, call, patch
import sys
import unittest


class TestHardware(unittest.TestCase):
    def setUp(self):
        self.time_patcher = patch('time.sleep')
        self.time_sleep = self.time_patcher.start()
        self.addCleanup(self.time_patcher.stop)

        self.gpio_patcher = patch('autodesk.hardware.GPIO')
        self.gpio = self.gpio_patcher.start()
        self.addCleanup(self.gpio_patcher.stop)

    def hardware(self):
        return Hardware(5, (0, 1), 2)

    def test_hardware_create(self):
        with self.hardware() as hw:
            self.gpio.setmode.assert_called_with(self.gpio.BOARD)
            self.gpio.setup.assert_has_calls([
                call(0, self.gpio.OUT),
                call(1, self.gpio.OUT),
                call(2, self.gpio.OUT)
            ])
            self.gpio.cleanup.assert_not_called()
        self.gpio.cleanup.assert_called_once()

    def test_hardware_go_down(self):
        with self.hardware() as hw:
            hw.go(Down())
            self.gpio.output.assert_has_calls([
                call(0, self.gpio.HIGH),
                call(0, self.gpio.LOW)
            ])
            self.time_sleep.assert_called_once_with(5)

    def test_hardware_go_up(self):
        with self.hardware() as hw:
            hw.go(Up())
            self.gpio.output.assert_has_calls([
                call(1, self.gpio.HIGH),
                call(1, self.gpio.LOW)
            ])
            self.time_sleep.assert_called_once_with(5)

    def test_hardware_light_on(self):
        with self.hardware() as hw:
            hw.light(Active())
            self.gpio.output.assert_called_once_with(2, self.gpio.HIGH)

    def test_hardware_light_off(self):
        with self.hardware() as hw:
            hw.light(Inactive())
            self.gpio.output.assert_called_once_with(2, self.gpio.LOW)
