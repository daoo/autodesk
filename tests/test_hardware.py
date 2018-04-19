from autodesk.hardware import create_hardware
from unittest.mock import patch, MagicMock
import unittest


def patch_module(module, mock):
    return patch.dict('sys.modules', {module: mock})


class TestHardware(unittest.TestCase):
    def test_create_hardware_raspberry_pi(self):
        raspberrypi = MagicMock()

        with patch_module('autodesk.hardware.raspberrypi', raspberrypi):
            create_hardware('raspberrypi', 5, (1, 2), 3)

        raspberrypi.RaspberryPi.assert_called_once_with(5, (1, 2), 3)

    def test_create_hardware_ft232h(self):
        ft232h = MagicMock()

        with patch_module('autodesk.hardware.ft232h', ft232h):
            create_hardware('ft232h', 5, (1, 2), 3)

        ft232h.Ft232h.assert_called_once_with(5, (1, 2), 3)

    def test_create_hardware_noop(self):
        noop = MagicMock()

        with patch.dict('sys.modules', {'autodesk.hardware.noop': noop}):
            create_hardware('noop', None, None, None)

        noop.Noop.assert_called_once_with()
