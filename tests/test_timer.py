from autodesk.model import Down, Up
from autodesk.timer import Timer
from datetime import timedelta
import tempfile
import unittest


class TestTimer(unittest.TestCase):
    def setUp(self):
        self.timer_file = tempfile.NamedTemporaryFile()
        self.timer_path = self.timer_file.name
        self.addCleanup(self.timer_file.close)

    def test_stop(self):
        Timer(self.timer_path).stop()
        with open(self.timer_path, 'r') as fobj:
            self.assertEqual(fobj.read(), 'stop\n')

    def test_schedule_down(self):
        Timer(self.timer_path).schedule(timedelta(seconds=42), Down())
        with open(self.timer_path, 'r') as fobj:
            self.assertEqual(fobj.read(), '42 0\n')

    def test_schedule_up(self):
        Timer(self.timer_path).schedule(timedelta(seconds=42), Up())
        with open(self.timer_path, 'r') as fobj:
            self.assertEqual(fobj.read(), '42 1\n')
