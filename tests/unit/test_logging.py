from autodesk.hardware.logging import LoggingWrapper
from autodesk.model import Up, Active
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
    hardware.desk(Up())
    inner.desk.assert_called_once_with(Up())


def test_light(inner, hardware):
    hardware.light(Active())
    inner.light.assert_called_once_with(Active())
