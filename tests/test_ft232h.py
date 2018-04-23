from autodesk.model import Down, Up, Active, Inactive
from unittest.mock import call, MagicMock
import tests.utils as utils


class TestFt232h(utils.TestCase):
    def setUp(self):
        self.time_sleep = self.patch('time.sleep')

        self.ft232h = MagicMock()
        self.device = self.ft232h.FT232H.return_value
        self.gpio = MagicMock()
        import sys
        sys.modules['Adafruit_GPIO'] = self.gpio
        self.addCleanup(sys.modules.pop, 'Adafruit_GPIO')
        sys.modules['FT232H'] = self.ft232h
        self.addCleanup(sys.modules.pop, 'FT232H')

        from autodesk.hardware.ft232h import Ft232h
        # Must also pop the ft232h module as it is cached and contains an
        # reference to the old mocked RPi import.
        self.addCleanup(sys.modules.pop, 'autodesk.hardware.ft232h')

        self.hw = Ft232h(5, (0, 1), 2)

    def test_constructor(self):
        # constructor called by setUp
        self.device.setup.assert_has_calls([
            call(0, self.gpio.OUT),
            call(1, self.gpio.OUT),
            call(2, self.gpio.OUT)
        ])

    def test_close(self):
        self.hw.close()
        self.device.close.assert_called_once()

    def test_desk_down(self):
        self.hw.desk(Down())
        self.device.output.assert_has_calls([
            call(0, self.gpio.HIGH),
            call(0, self.gpio.LOW)
        ])
        self.time_sleep.assert_called_once_with(5)

    def test_desk_up(self):
        self.hw.desk(Up())
        self.device.output.assert_has_calls([
            call(1, self.gpio.HIGH),
            call(1, self.gpio.LOW)
        ])
        self.time_sleep.assert_called_once_with(5)

    def test_light_on(self):
        self.hw.light(Active())
        self.device.output.assert_called_once_with(2, self.gpio.HIGH)

    def test_light_off(self):
        self.hw.light(Inactive())
        self.device.output.assert_called_once_with(2, self.gpio.LOW)
