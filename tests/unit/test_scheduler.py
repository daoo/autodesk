from pandas import Timedelta

from autodesk.scheduler import Scheduler
from autodesk.states import DOWN, UP


def test_active_for_30minutes_with_60minute_limit_and_desk_down():
    active_time = Timedelta(minutes=30)
    limits = (Timedelta(minutes=60), Timedelta(minutes=30))
    scheduler = Scheduler(limits)

    delay = scheduler.compute_delay(active_time, DOWN)

    assert delay == Timedelta(minutes=30)


def test_active_for_30minutes_with_30minute_limit_and_desk_up():
    active_time = Timedelta(minutes=30)
    limits = (Timedelta(minutes=60), Timedelta(minutes=30))
    scheduler = Scheduler(limits)

    delay = scheduler.compute_delay(active_time, UP)

    assert delay == Timedelta(0)
