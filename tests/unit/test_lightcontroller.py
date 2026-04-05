import pytest

from autodesk.hardware.noop import NoopPin
from autodesk.lightcontroller import LightController
from autodesk.states import Session


@pytest.fixture
def pin_mock(mocker):
    return mocker.create_autospec(NoopPin, instance=True)


def test_set_inactive(pin_mock):
    service = LightController(pin_mock)

    service.set(Session.INACTIVE)

    pin_mock.write.assert_called_once_with(0)


def test_set_active(pin_mock):
    service = LightController(pin_mock)

    service.set(Session.ACTIVE)

    pin_mock.write.assert_called_once_with(1)
