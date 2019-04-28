from autodesk.hardware.noop import Noop
from autodesk.states import UP, ACTIVE


def test_constructor():
    Noop()


def test_close():
    Noop().close()


def test_desk():
    Noop().desk(UP)


def test_light():
    Noop().light(ACTIVE)
