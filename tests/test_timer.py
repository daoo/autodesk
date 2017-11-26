from autodesk.model import Down, Up
from autodesk.timer import Timer
from datetime import timedelta
from unittest.mock import MagicMock
import time
import unittest


class TestTimer(unittest.TestCase):
    def setUp(self):
        self.timer = Timer()
        self.action = MagicMock()
        self.timer.set_action(self.action)

    def test_stop(self):
        self.timer.schedule(timedelta(seconds=0.05), Down())
        self.timer.stop()
        time.sleep(0.1)
        self.action.assert_not_called()

    def test_schedule_down(self):
        self.timer.schedule(timedelta(seconds=0), Down())
        self.action.assert_called_with(Down())

    def test_schedule_up(self):
        self.timer.schedule(timedelta(seconds=0), Up())
        self.action.assert_called_with(Up())

    def test_overwrite(self):
        self.timer.schedule(timedelta(seconds=1), Up())
        self.timer.schedule(timedelta(seconds=0), Down())
        self.action.assert_called_with(Down())
