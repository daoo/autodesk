from autodesk.model import Down, Up, Active, Inactive
from unittest.mock import call, MagicMock
import tests.utils as utils


class TestRaspberryPi(utils.TestCase):
    def setUp(self):
        self.time_sleep = self.patch('time.sleep')

        rpi = MagicMock()
        self.gpio = rpi.GPIO
        import sys
        sys.modules['RPi'] = rpi
        self.addCleanup(sys.modules.pop, 'RPi')
        sys.modules['RPi.GPIO'] = self.gpio
        self.addCleanup(sys.modules.pop, 'RPi.GPIO')

        from autodesk.hardware.raspberrypi import RaspberryPi
        # Must also pop the raspberrypi module as it is cached and contains an
        # reference to the old mocked RPi import.
        self.addCleanup(sys.modules.pop, 'autodesk.hardware.raspberrypi')

        self.hw = RaspberryPi(5, (0, 1), 2)

    def test_raspberrypi_constructor(self):
        # constructor called by setUp
        self.gpio.setmode.assert_called_once_with(self.gpio.BOARD)
        self.gpio.setup.assert_has_calls([
            call(0, self.gpio.OUT),
            call(1, self.gpio.OUT),
            call(2, self.gpio.OUT)
        ])

    def test_raspberrypi_close(self):
        self.hw.close()
        self.gpio.cleanup.assert_called_once()

    def test_raspberrypi_desk_down(self):
        self.hw.desk(Down())
        self.gpio.output.assert_has_calls([
            call(0, self.gpio.HIGH),
            call(0, self.gpio.LOW)
        ])
        self.time_sleep.assert_called_once_with(5)

    def test_raspberrypi_desk_up(self):
        self.hw.desk(Up())
        self.gpio.output.assert_has_calls([
            call(1, self.gpio.HIGH),
            call(1, self.gpio.LOW)
        ])
        self.time_sleep.assert_called_once_with(5)

    def test_raspberrypi_light_on(self):
        self.hw.light(Active())
        self.gpio.output.assert_called_once_with(2, self.gpio.HIGH)

    def test_raspberrypi_light_off(self):
        self.hw.light(Inactive())
        self.gpio.output.assert_called_once_with(2, self.gpio.LOW)
