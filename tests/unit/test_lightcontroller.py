import pytest

from autodesk.lightcontroller import LightController
from autodesk.states import ACTIVE, INACTIVE


@pytest.fixture
def pin_mock(mocker):
    return mocker.patch("autodesk.hardware.noop.NoopPin", autospec=True)


def test_set_inactive(pin_mock):
    service = LightController(pin_mock)

    service.set(INACTIVE)

    pin_mock.write.assert_called_once_with(0)


def test_set_active(pin_mock):
    service = LightController(pin_mock)

    service.set(ACTIVE)

    pin_mock.write.assert_called_once_with(1)
