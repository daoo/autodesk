from autodesk.model import Inactive, Active, Down, Up
from autodesk.spans import Span
from datetime import datetime, timedelta
from unittest.mock import patch
import autodesk.stats as stats
import unittest

class TestStats(unittest.TestCase):
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

    def test_group_into_days_identity(self):
        spans = [Span(
            datetime(2017, 4, 12, 10, 0, 0),
            datetime(2017, 4, 12, 10, 30, 0),
            Active()
        )]
        flatten = lambda l: [item for sublist in l for item in sublist]
        daily_active_time = stats.compute_daily_active_time(spans)
        self.assertEqual(
            flatten(stats.group_into_days(daily_active_time)),
            daily_active_time
        )

    def test_compute_active_time_empty(self):
        self.assertRaises(IndexError, stats.compute_active_time, [], [])

    def test_compute_active_time_inactive(self):
        desk_span = Span(
            datetime.fromtimestamp(0),
            datetime.fromtimestamp(1000),
            Down())
        session_span = Span(
            datetime.fromtimestamp(0),
            datetime.fromtimestamp(1000),
            Inactive())
        self.assertEqual(
            stats.compute_active_time([session_span], [desk_span]),
            timedelta(0)
        )

    def test_compute_active_time_active(self):
        desk_span = Span(
            datetime.fromtimestamp(0),
            datetime.fromtimestamp(1000),
            Down())
        session_span = Span(
            datetime.fromtimestamp(0),
            datetime.fromtimestamp(1000),
            Active())
        self.assertEqual(
            stats.compute_active_time([session_span], [desk_span]),
            timedelta(seconds=1000)
        )
