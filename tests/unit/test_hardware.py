from autodesk.hardware import create_pin_factory


def patch_module(mocker, module: str):
    fake = mocker.MagicMock()
    mocker.patch.dict("sys.modules", {module: fake})
    return fake


def test_create_pin_factory_raspberry_pi(mocker):
    raspberrypi_mock = patch_module(mocker, "autodesk.hardware.raspberrypi")

    create_pin_factory("raspberrypi")

    raspberrypi_mock.RaspberryPiPinFactory.assert_called_once()


def test_create_pin_factory_ft232h(mocker):
    ft232h_mock = patch_module(mocker, "autodesk.hardware.ft232h")

    create_pin_factory("ft232h")

    ft232h_mock.Ft232hPinFactory.assert_called_once()


def test_create_pin_factory_noop(mocker):
    noop_mock = patch_module(mocker, "autodesk.hardware.noop")

    create_pin_factory("noop")

    noop_mock.NoopPinFactory.assert_called_once()
