from autodesk.controller import Controller, allow_desk_operation
from autodesk.spans import Event
from contextlib import closing
from datetime import date, datetime, time, timedelta
from unittest.mock import patch
import autodesk.model as model
import pytest
import tempfile


LIMITS = (timedelta(minutes=50), timedelta(minutes=10))


@pytest.fixture
def hardware():
    with patch('autodesk.hardware.Hardware') as mockhw:
        yield mockhw


@pytest.fixture
def database():
    with tempfile.NamedTemporaryFile() as tmp:
        with closing(model.Database(tmp.name)) as database:
            yield database


@pytest.fixture
def timer():
    with patch('autodesk.timer.Timer') as mocktimer:
        yield mocktimer


def test_allow_operation_workday():
    monday = date(2017, 2, 13)
    tuesday = date(2017, 2, 14)
    wednesday = date(2017, 2, 15)
    thursday = date(2017, 2, 16)
    friday = date(2017, 2, 17)
    stroke = time(12, 0, 0)
    assert allow_desk_operation(datetime.combine(monday, stroke))
    assert allow_desk_operation(datetime.combine(tuesday, stroke))
    assert allow_desk_operation(datetime.combine(wednesday, stroke))
    assert allow_desk_operation(datetime.combine(thursday, stroke))
    assert allow_desk_operation(datetime.combine(friday, stroke))


def test_disallow_operation_night_time():
    workday = datetime(2017, 2, 13)
    assert not allow_desk_operation(datetime.combine(workday, time(8, 59, 0)))
    assert not allow_desk_operation(datetime.combine(workday, time(17, 1, 0)))
    assert not allow_desk_operation(datetime.combine(workday, time(23, 0, 0)))
    assert not allow_desk_operation(datetime.combine(workday, time(3, 0, 0)))
    assert not allow_desk_operation(datetime.combine(workday, time(6, 0, 0)))


def test_disallow_operation_weekend():
    saturday = date(2017, 2, 18)
    sunday = date(2017, 2, 19)
    stroke = time(12, 0, 0)
    assert not allow_desk_operation(datetime.combine(saturday, stroke))
    assert not allow_desk_operation(datetime.combine(sunday, stroke))


def test_update_timer(database, timer):
    controller = Controller(None, LIMITS, timer, database)

    initial = datetime(2017, 2, 13, 11, 00, 0)
    activated_at = datetime(2017, 2, 13, 11, 50, 0)
    now = datetime(2017, 2, 13, 12, 0, 0)

    controller.update_timer(initial)
    assert timer.stop.called

    controller.set_session(activated_at, model.Active())
    assert timer.set.call_args == ((timedelta(seconds=3000), model.Up()),)

    controller.update_timer(now)
    assert timer.set.call_args == ((timedelta(seconds=2400), model.Up()),)


def test_set_session(database, timer):
    controller = Controller(None, LIMITS, timer, database)
    events = [
        Event(datetime(2017, 2, 13, 12, 0, 0), model.Active()),
        Event(datetime(2017, 2, 13, 13, 0, 0), model.Inactive())
    ]
    for event in events:
        controller.set_session(event.index, event.data)
    assert database.get_session_events() == events


def test_set_desk(hardware, database, timer, capsys):
    controller = Controller(hardware, LIMITS, timer, database)
    events = [
        Event(datetime(2017, 2, 13, 12, 0, 0), model.Up()),
        Event(datetime(2017, 2, 13, 12, 0, 0), model.Down())
    ]
    for event in events:
        controller.set_desk(event.index, event.data)
        assert hardware.setup.called
        assert hardware.go.call_args[0] == (event.data,)
        assert hardware.cleanup.called
    assert database.get_desk_events() == events
