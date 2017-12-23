from autodesk.model import Down, Up, Inactive, Active
from autodesk.spans import Span
from autodesk.timer import Communicator, Timer
from datetime import datetime, timedelta
from unittest.mock import patch
import tempfile
import unittest


class TestCommunicator(unittest.TestCase):
    def setUp(self):
        timer_file = tempfile.NamedTemporaryFile()
        self.timer_path = timer_file.name
        self.addCleanup(timer_file.close)

    def test_communicator_cancel(self):
        Communicator(self.timer_path).cancel()
        with open(self.timer_path, 'r') as fobj:
            self.assertEqual(fobj.read(), 'cancel\n')

    def test_communicator_schedule_down(self):
        Communicator(self.timer_path).schedule(timedelta(seconds=42), Down())
        with open(self.timer_path, 'r') as fobj:
            self.assertEqual(fobj.read(), '42 0\n')

    def test_communicator_schedule_up(self):
        Communicator(self.timer_path).schedule(timedelta(seconds=42), Up())
        with open(self.timer_path, 'r') as fobj:
            self.assertEqual(fobj.read(), '42 1\n')


class TestTimer(unittest.TestCase):
    def setUp(self):
        limits = (timedelta(minutes=50), timedelta(minutes=10))

        communicator_patcher = patch(
            'autodesk.timer.Communicator', autospec=True)
        self.communicator = communicator_patcher.start()
        self.addCleanup(communicator_patcher.stop)

        database_patcher = patch(
            'autodesk.model.Database', autospec=True)
        self.database = database_patcher.start()
        self.addCleanup(database_patcher.stop)

        self.beginning = datetime.fromtimestamp(0)
        self.now = datetime(2017, 4, 14, 10, 0, 0)
        self.database.get_desk_spans.return_value = [
            Span(self.beginning, self.now, Down())
        ]
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, Inactive())
        ]

        self.timer = Timer(limits, self.communicator, self.database)

    def test_timer_update_inactive(self):
        self.timer.update(self.now)
        self.communicator.cancel.assert_called_once()
        self.database.get_desk_spans.assert_not_called()

    @patch('autodesk.timer.stats.compute_active_time', autospec=True)
    def test_timer_update_active(self, compute_active_time):
        compute_active_time.return_value = timedelta(0)
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, Active())
        ]
        self.timer.update(self.now)
        self.communicator.schedule.assert_called_with(timedelta(minutes=50),
                                                      Up())

    @patch('autodesk.timer.stats.compute_active_time', autospec=True)
    def test_timer_update_active_with_duration(self, compute_active_time):
        compute_active_time.return_value = timedelta(minutes=10)
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, Active())
        ]
        self.timer.update(self.now)
        self.communicator.schedule.assert_called_with(timedelta(minutes=40),
                                                      Up())
