from autodesk.hardware.noop import Noop
from autodesk.model import Up, Active


def test_constructor():
    Noop()


def test_close():
    Noop().close()


def test_desk():
    Noop().desk(Up())


def test_light():
    Noop().light(Active())
