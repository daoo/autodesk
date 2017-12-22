from autodesk.hardware import Hardware
from autodesk.model import Down, Up, Active, Inactive
from unittest.mock import MagicMock, call, patch
import sys
import unittest


class TestHardware(unittest.TestCase):
    def setUp(self):
        time_patcher = patch('time.sleep')
        self.time_sleep = time_patcher.start()
        self.addCleanup(time_patcher.stop)

        gpio_patcher = patch('autodesk.hardware.GPIO')
        self.gpio = gpio_patcher.start()
        self.addCleanup(gpio_patcher.stop)

        self.hardware = Hardware(5, (0, 1), 2)

    def test_hardware_init(self):
        self.hardware.init()
        self.gpio.setmode.assert_called_with(self.gpio.BOARD)
        self.gpio.setup.assert_has_calls([
            call(0, self.gpio.OUT),
            call(1, self.gpio.OUT),
            call(2, self.gpio.OUT)
        ])

    def test_hardware_close(self):
        self.hardware.close()
        self.gpio.cleanup.assert_called_once()

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

    def test_hardware_light_on(self):
        self.hardware.light(Active())
        self.gpio.output.assert_called_once_with(2, self.gpio.HIGH)

    def test_hardware_light_off(self):
        self.hardware.light(Inactive())
        self.gpio.output.assert_called_once_with(2, self.gpio.LOW)
