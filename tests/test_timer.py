from autodesk.model import Down, Up, Inactive, Active
from autodesk.spans import Span
from autodesk.timer import Timer
from datetime import datetime, timedelta
from unittest.mock import patch
import unittest


class TestTimer(unittest.TestCase):
    def setUp(self):
        limits = (timedelta(minutes=50), timedelta(minutes=10))

        factory_patcher = patch(
            'autodesk.timer.TimerFactory', autospec=True)
        self.factory = factory_patcher.start()
        self.addCleanup(factory_patcher.stop)

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

        self.timer = Timer(limits, self.database, self.factory)

    def test_timer_update_inactive(self):
        self.timer.update(self.now)
        self.factory.start.assert_not_called()
        self.database.get_desk_spans.assert_not_called()

    def test_timer_update_active(self):
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, Inactive()),
            Span(self.now, self.now, Active()),
        ]
        self.timer.update(self.now)
        self.factory.start.assert_called_with(timedelta(minutes=50), Up())

    def test_timer_update_active_with_duration(self):
        later = self.now + timedelta(minutes=10)
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, Inactive()),
            Span(self.now, later, Active()),
        ]
        self.database.get_desk_spans.return_value = [
            Span(self.beginning, later, Down())
        ]
        self.timer.update(self.now)
        self.factory.start.assert_called_with(timedelta(minutes=40), Up())
