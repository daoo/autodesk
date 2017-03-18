from autodesk.spans import Event
from contextlib import closing
from datetime import date, datetime, time, timedelta
from autodesk.controller import Controller, allow_desk_operation
import autodesk.model as model
import pytest
import tempfile


PINS = (15, 13)
LIMITS = (timedelta(minutes=50), timedelta(minutes=10))


@pytest.fixture
def database():
    with tempfile.NamedTemporaryFile() as tmp:
        with closing(model.Database(tmp.name)) as database:
            yield database


@pytest.fixture
def timer_path():
    with tempfile.NamedTemporaryFile() as tmp:
        yield tmp.name


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


def test_update_timer(database, timer_path):
    controller = Controller(PINS, LIMITS, timer_path, database)

    initial = datetime(2017, 2, 13, 11, 00, 0)
    activated_at = datetime(2017, 2, 13, 11, 50, 0)
    now = datetime(2017, 2, 13, 12, 0, 0)

    controller.update_timer(initial)
    with open(timer_path, 'r') as timer_file:
        assert 'stop\n' == timer_file.read()

    controller.set_session(activated_at, model.Active())
    with open(timer_path, 'r') as timer_file:
        str = timer_file.read()
        assert '3000 1\n' == str

    controller.update_timer(now)
    with open(timer_path, 'r') as timer_file:
        str = timer_file.read()
        assert '2400 1\n' == str


def test_set_session(database, timer_path):
    controller = Controller(PINS, LIMITS, timer_path, database)
    events = [
        Event(datetime(2017, 2, 13, 12, 0, 0), model.Active()),
        Event(datetime(2017, 2, 13, 13, 0, 0), model.Inactive())
    ]
    for event in events:
        controller.set_session(event.index, event.data)
    assert database.get_session_events() == events


expected = """Warning: GPIO not found, using test implementation.
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.output(13, GPIO.HIGH)
GPIO.output(13, GPIO.LOW)
GPIO.cleanup()
Warning: GPIO not found, using test implementation.
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.output(15, GPIO.HIGH)
GPIO.output(15, GPIO.LOW)
GPIO.cleanup()
"""


def test_set_desk(database, timer_path, capsys):
    controller = Controller(PINS, LIMITS, timer_path, database)
    events = [
        Event(datetime(2017, 2, 13, 12, 0, 0), model.Up()),
        Event(datetime(2017, 2, 13, 12, 0, 0), model.Down())
    ]
    for event in events:
        controller.set_desk(event.index, event.data)
    out = capsys.readouterr()[0]
    assert database.get_desk_events() == events
    assert out == expected
