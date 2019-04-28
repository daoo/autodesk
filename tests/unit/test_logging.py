from autodesk.hardware.logging import LoggingWrapper
from autodesk.states import UP, ACTIVE
import pytest


@pytest.fixture
def inner(mocker):
    return mocker.Mock()


@pytest.fixture
def hardware(inner):
    return LoggingWrapper(inner)


def test_close(inner, hardware):
    hardware.close()
    inner.close.assert_called_once()


def test_desk(inner, hardware):
    hardware.desk(UP)
    inner.desk.assert_called_once_with(UP)


def test_light(inner, hardware):
    hardware.light(ACTIVE)
    inner.light.assert_called_once_with(ACTIVE)
