from autodesk.operation import Operation
from datetime import date, time
from pandas import Timestamp
import pytest


def combine(dates, times):
    return [Timestamp.combine(day, stroke)
            for day in dates for stroke in times]


ondates = [
    date(2017, 2, 13),  # monday
    date(2017, 2, 14),  # tuesday
    date(2017, 2, 15),  # wednesday
    date(2017, 2, 16),  # thursday
    date(2017, 2, 17),  # friday
]

offdates = [
    date(2017, 2, 18),  # saturday
    date(2017, 2, 19),  # sunday
]

ontimes = [
    time(8, 0, 0),
    time(11, 34, 0),
    time(13, 38, 0),
    time(17, 30, 0),
    time(18, 0, 0),
]

offtimes = [
    time(7, 59, 0),
    time(18, 1, 0),
    time(23, 0, 0),
    time(3, 0, 0),
    time(6, 0, 0),
]

ondatetimes = combine(ondates, ontimes)
offdatetimes = \
    combine(offdates, offtimes) + \
    combine(ondates, offtimes) + \
    combine(offdates, ontimes)


@pytest.mark.parametrize("at", ondatetimes)
def test_operation_allow(at):
    assert Operation().allowed(at)


@pytest.mark.parametrize("at", offdatetimes)
def test_operation_disallow(at):
    assert not Operation().allowed(at)
