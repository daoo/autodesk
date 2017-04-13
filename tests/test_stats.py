from autodesk.model import Active
from autodesk.spans import Span
from datetime import datetime
from unittest.mock import patch
import autodesk.stats as stats
import unittest

class TestStats(unittest.TestCase):
    def test_compute_daily_active_time_empty(self):
        self.assertEqual(
            sum(stats.compute_daily_active_time([])), 0)

    def test_compute_daily_active_time_sum(self):
        spans = [Span(
            datetime(2017, 4, 12, 10, 0, 0),
            datetime(2017, 4, 12, 10, 30, 0),
            Active()
        )]
        self.assertEqual(
            sum(stats.compute_daily_active_time(spans)),
            30
        )

