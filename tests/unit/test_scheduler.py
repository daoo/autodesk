from datetime import timedelta

from autodesk.scheduler import Scheduler
from autodesk.states import DOWN, UP


def test_active_for_30minutes_with_60minute_limit_and_desk_down():
    active_time = timedelta(minutes=30)
    limits = (timedelta(minutes=60), timedelta(minutes=30))
    scheduler = Scheduler(limits)

    delay = scheduler.compute_delay(active_time, DOWN)

    assert delay == timedelta(minutes=30)


def test_active_for_30minutes_with_30minute_limit_and_desk_up():
    active_time = timedelta(minutes=30)
    limits = (timedelta(minutes=60), timedelta(minutes=30))
    scheduler = Scheduler(limits)

    delay = scheduler.compute_delay(active_time, UP)

    assert delay == timedelta(0)
