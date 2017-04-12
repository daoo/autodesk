from autodesk.model import Active
from autodesk.spans import Span
from autodesk.stats import Stats
from datetime import datetime
from unittest.mock import patch
import unittest

class TestStats(unittest.TestCase):
    def setUp(self):
        self.database_patcher = patch(
            'autodesk.model.Database', autospec=True)
        self.database = self.database_patcher.start()
        self.addCleanup(self.database_patcher.stop)

        self.stats = Stats(self.database)

    def test_compute_daily_active_time_empty(self):
        self.assertEqual(sum(self.stats.compute_daily_active_time(
            datetime.fromtimestamp(0),
            datetime.fromtimestamp(10000000)
        )), 0)

    def test_compute_daily_active_time_sum(self):
        inital = datetime.fromtimestamp(0)
        final = datetime(2017, 4, 12, 11, 30, 0)
        spans = [Span(
            datetime(2017, 4, 12, 10, 0, 0),
            datetime(2017, 4, 12, 10, 30, 0),
            Active()
        )]
        self.database.get_session_spans.return_value = spans
        self.assertEqual(
            sum(self.stats.compute_daily_active_time(inital, final)),
            30
        )

