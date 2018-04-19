from autodesk.hardware.logging import LoggingWrapper
from autodesk.model import Up, Active
from unittest.mock import MagicMock
import unittest


class TestLoggingWrapper(unittest.TestCase):
    def setUp(self):
        self.inner = MagicMock()
        self.hardware = LoggingWrapper(self.inner)

    def test_logging_wrapper_close(self):
        self.hardware.close()
        self.inner.close.assert_called_once()

    def test_logging_wrapper_desk(self):
        self.hardware.desk(Up())
        self.inner.desk.assert_called_once_with(Up())

    def test_logging_wrapper_light(self):
        self.hardware.light(Active())
        self.inner.light.assert_called_once_with(Active())
