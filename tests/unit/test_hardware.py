from autodesk.hardware import create_hardware
import mock


def patch_module(module, module_mock):
    return mock.patch.dict('sys.modules', {module: module_mock})


def test_create_hardware_raspberry_pi():
    raspberrypi = mock.MagicMock()

    with patch_module('autodesk.hardware.raspberrypi', raspberrypi):
        create_hardware('raspberrypi', 5, (1, 2), 3)

    raspberrypi.RaspberryPi.assert_called_once_with(5, (1, 2), 3)


def test_create_hardware_ft232h():
    ft232h = mock.MagicMock()

    with patch_module('autodesk.hardware.ft232h', ft232h):
        create_hardware('ft232h', 5, (1, 2), 3)

    ft232h.Ft232h.assert_called_once_with(5, (1, 2), 3)


def test_create_hardware_noop():
    noop = mock.MagicMock()

    with patch_module('autodesk.hardware.noop', noop):
        create_hardware('noop', None, None, None)

    noop.Noop.assert_called_once_with()
