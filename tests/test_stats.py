from autodesk.model import Inactive, Active, Down, Up
from autodesk.spans import Span
from datetime import datetime, timedelta
from unittest.mock import patch
import autodesk.stats as stats
import unittest


class TestStats(unittest.TestCase):
    def test_stats_compute_daily_active_time_sum(self):
        spans = [Span(
            datetime(2017, 4, 12, 10, 0, 0),
            datetime(2017, 4, 12, 10, 30, 0),
            Active()
        )]
        self.assertEqual(
            sum(stats.compute_daily_active_time(spans)),
            30
        )

    def test_stats_compute_daily_active_time_inactive_zero(self):
        spans = [Span(
            datetime(2017, 4, 12, 10, 0, 0),
            datetime(2017, 4, 12, 10, 30, 0),
            Inactive()
        )]
        self.assertEqual(sum(stats.compute_daily_active_time(spans)), 0)

    def test_stats_group_into_days_identity(self):
        spans = [Span(
            datetime(2017, 4, 12, 10, 0, 0),
            datetime(2017, 4, 12, 10, 30, 0),
            Active()
        )]

        def flatten(l):
            return [item for sublist in l for item in sublist]

        daily_active_time = stats.compute_daily_active_time(spans)
        self.assertEqual(
            flatten(stats.group_into_days(daily_active_time)),
            daily_active_time
        )
