from autodesk.hardware.noop import Noop
from autodesk.model import Up, Active
import unittest


class TestNoop(unittest.TestCase):
    def test_constructor(self):
        Noop()

    def test_close(self):
        Noop().close()

    def test_desk(self):
        Noop().desk(Up())

    def test_light(self):
        Noop().light(Active())
