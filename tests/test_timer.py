from autodesk.model import Down, Up
from autodesk.timer import Timer
from datetime import timedelta
import tempfile
import unittest


class TestTimer(unittest.TestCase):
    def setUp(self):
        timer_file = tempfile.NamedTemporaryFile()
        self.timer_path = timer_file.name
        self.addCleanup(timer_file.close)

    def test_cancel(self):
        Timer(self.timer_path).cancel()
        with open(self.timer_path, 'r') as fobj:
            self.assertEqual(fobj.read(), 'cancel\n')

    def test_schedule_down(self):
        Timer(self.timer_path).schedule(timedelta(seconds=42), Down())
        with open(self.timer_path, 'r') as fobj:
            self.assertEqual(fobj.read(), '42 0\n')

    def test_schedule_up(self):
        Timer(self.timer_path).schedule(timedelta(seconds=42), Up())
        with open(self.timer_path, 'r') as fobj:
            self.assertEqual(fobj.read(), '42 1\n')
