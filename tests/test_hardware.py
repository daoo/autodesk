from autodesk.hardware import create_hardware
from unittest.mock import patch, MagicMock
import unittest


def config(hardware):
    return {
        'desk': {
            'hardware': hardware,
            'delay': 5,
            'motor_pins': {'down': 1, 'up': 2},
            'light_pin': 3,
        }
    }


def patch_module(module, mock):
    return patch.dict('sys.modules', {module: mock})


class TestRaspberryPi(unittest.TestCase):
    def test_create_hardware_raspberry_pi(self):
        raspberrypi = MagicMock()

        with patch_module('autodesk.hardware.raspberrypi', raspberrypi):
            create_hardware(config('raspberrypi'))

        raspberrypi.RaspberryPi.assert_called_once_with(5, (1, 2), 3)

    def test_create_hardware_ft232h(self):
        ft232h = MagicMock()

        with patch_module('autodesk.hardware.ft232h', ft232h):
            create_hardware(config('ft232h'))

        ft232h.Ft232h.assert_called_once_with(5, (1, 2), 3)

    def test_create_hardware_noop(self):
        noop = MagicMock()

        with patch.dict('sys.modules', {'autodesk.hardware.noop': noop}):
            create_hardware(config('noop'))

        noop.Noop.assert_called_once_with()
