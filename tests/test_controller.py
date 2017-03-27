from autodesk.controller import Controller, allow_desk_operation
from autodesk.spans import Event
from datetime import date, datetime, time, timedelta
from unittest.mock import patch
import autodesk.model as model
import pytest


LIMITS = (timedelta(minutes=50), timedelta(minutes=10))


@pytest.fixture
def hardware():
    with patch('autodesk.hardware.Hardware') as mockhw:
        yield mockhw


@pytest.fixture
def database():
    with patch('autodesk.model.Database') as mockdb:
        with patch('autodesk.model.Snapshot') as mocksnap:
            mockdb.get_snapshot.return_value = mocksnap
            mocksnap.get_active_time.return_value = timedelta(0)
            mocksnap.get_latest_desk_state.return_value = model.Down()
            mocksnap.get_latest_session_state.return_value = model.Inactive()
            yield (mockdb, mocksnap)


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
    (mockdb, mocksnap) = database
    controller = Controller(None, LIMITS, timer, mockdb)

    time0 = datetime.fromtimestamp(0)
    time1 = datetime(2017, 2, 13, 11, 0, 0)
    snapshot_args = {'initial': time0, 'final': time1}

    controller.update_timer(time1)
    assert mockdb.get_snapshot.call_args == ((), snapshot_args)
    assert timer.stop.called

    mocksnap.get_latest_session_state.return_value = model.Active()
    controller.update_timer(time1)
    assert mockdb.get_snapshot.call_args == ((), snapshot_args)
    assert timer.set.call_args == ((timedelta(seconds=3000), model.Up()),)

    mocksnap.get_active_time.return_value = timedelta(seconds=1000)
    controller.update_timer(time1)
    assert mockdb.get_snapshot.call_args == ((), snapshot_args)
    assert timer.set.call_args == ((timedelta(seconds=2000), model.Up()),)


def test_set_session(database, timer):
    (mockdb, _) = database
    controller = Controller(None, LIMITS, timer, mockdb)

    event1 = Event(datetime(2017, 2, 13, 12, 0, 0), model.Active())
    controller.set_session(event1.index, event1.data)
    assert mockdb.insert_session_event.call_args[0] == (event1,)

    event2 = Event(datetime(2017, 2, 13, 13, 0, 0), model.Inactive())
    controller.set_session(event2.index, event2.data)
    assert mockdb.insert_session_event.call_args[0] == (event2,)


def test_set_desk(hardware, database, timer):
    (mockdb, _) = database
    controller = Controller(hardware, LIMITS, timer, mockdb)

    event1 = Event(datetime(2017, 2, 13, 12, 0, 0), model.Up())
    controller.set_desk(event1.index, event1.data)
    assert mockdb.insert_desk_event.call_args[0] == (event1,)
    assert hardware.setup.called
    assert hardware.go.call_args[0] == (event1.data,)
    assert hardware.cleanup.called

    event2 = Event(datetime(2017, 2, 13, 12, 0, 0), model.Down())
    controller.set_desk(event2.index, event2.data)
    assert mockdb.insert_desk_event.call_args[0] == (event2,)
    assert hardware.setup.called
    assert hardware.go.call_args[0] == (event2.data,)
    assert hardware.cleanup.called


def test_set_desk_disallow(hardware, database, timer):
    (mockdb, _) = database
    controller = Controller(hardware, LIMITS, timer, mockdb)

    event = Event(datetime(2017, 2, 13, 7, 0, 0), model.Down())
    controller.set_desk(event.index, event.data)
    assert not mockdb.insert_desk_event.called
    assert not hardware.setup.called
    assert not hardware.go.called
    assert not hardware.cleanup.called
    assert timer.stop.called
