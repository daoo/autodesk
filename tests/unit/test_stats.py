from autodesk.model import Inactive, Active
from autodesk.spans import Span
from datetime import datetime
import autodesk.stats as stats


def test_compute_hourly_relative_frequency_sum():
    spans = [Span(
        datetime(2017, 4, 12, 10, 0, 0),
        datetime(2017, 4, 12, 10, 30, 0),
        Active()
    )]
    result = stats.compute_hourly_relative_frequency(spans)
    assert result.values.sum() == 1


def test_compute_hourly_relative_frequency_inactive_zero():
    spans = [Span(
        datetime(2017, 4, 12, 10, 0, 0),
        datetime(2017, 4, 12, 10, 30, 0),
        Inactive()
    )]
    result = stats.compute_hourly_relative_frequency(spans)
    assert result.values.sum() == 0
