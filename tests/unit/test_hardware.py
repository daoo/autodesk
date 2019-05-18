from autodesk.hardware import create_hardware


def patch_module(mocker, module):
    fake = mocker.MagicMock()
    mocker.patch.dict('sys.modules', {module: fake})
    return fake


def test_create_hardware_raspberry_pi(mocker):
    raspberrypi_mock = patch_module(mocker, 'autodesk.hardware.raspberrypi')

    create_hardware('raspberrypi', 5, (1, 2), 3)

    raspberrypi_mock.RaspberryPi.assert_called_once_with(5, (1, 2), 3)


def test_create_hardware_ft232h(mocker):
    ft232h_mock = patch_module(mocker, 'autodesk.hardware.ft232h')

    create_hardware('ft232h', 5, (1, 2), 3)

    ft232h_mock.Ft232h.assert_called_once_with(5, (1, 2), 3)


def test_create_hardware_noop(mocker):
    noop_mock = patch_module(mocker, 'autodesk.hardware.noop')

    create_hardware('noop', None, None, None)

    noop_mock.Noop.assert_called_once_with()
