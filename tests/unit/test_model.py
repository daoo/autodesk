from autodesk.model import Model, Up, Down, Active, Inactive
from autodesk.model import session_from_int, desk_from_int, event_from_row
from autodesk.spans import Event, Span
from datetime import datetime, timedelta
import pytest


def test_down_next():
    assert Down().next() == Up()


def test_down_test():
    assert Down().test(0, 1) == 0


def test_up_next():
    assert Up().next() == Down()


def test_up_test():
    assert Up().test(0, 1) == 1


def test_session_from_int():
    assert session_from_int(0) == Inactive()
    assert session_from_int(1) == Active()
    with pytest.raises(ValueError):
        session_from_int(2)


def test_desk_from_int():
    assert desk_from_int(0) == Down()
    assert desk_from_int(1) == Up()
    with pytest.raises(ValueError):
        desk_from_int(2)


def test_event_from_row_incorrect(mocker):
    cursor = mocker.MagicMock()
    cursor.description = [['date'], ['foobar']]
    values = [0, 0]
    with pytest.raises(ValueError):
        event_from_row(cursor, values)


@pytest.fixture()
def model():
    model = Model(':memory:')
    yield model
    model.close()


def test_empty_events(model):
    assert model.get_desk_events() == []
    assert model.get_session_events() == []


def test_empty_spans(model):
    a = datetime.min
    b = datetime.max
    assert model.get_desk_spans(a, b) == [Span(a, b, Down())]
    assert model.get_session_spans(a, b) == [Span(a, b, Inactive())]


def test_set_desk(model):
    event = Event(datetime(2017, 1, 1), Up())
    model.set_desk(event)
    assert model.get_desk_events() == [event]


def test_set_session(model):
    event = Event(datetime(2017, 1, 1), Active())
    model.set_session(event)
    assert model.get_session_events() == [event]


def test_get_desk_spans(model):
    a = datetime(2018, 1, 1)
    b = datetime(2018, 1, 2)
    c = datetime(2018, 1, 3)
    model.set_desk(Event(b, Up()))
    assert model.get_desk_spans(a, c) == [Span(a, b, Down()), Span(b, c, Up())]


def test_get_session_spans(model):
    a = datetime(2018, 1, 1)
    b = datetime(2018, 1, 2)
    c = datetime(2018, 1, 3)
    model.set_session(Event(b, Active()))
    expected = [Span(a, b, Inactive()), Span(b, c, Active())]
    assert model.get_session_spans(a, c) == expected


def test_get_session_state_empty(model):
    assert model.get_session_state() == Inactive()


def test_get_session_state_active(model):
    event = Event(datetime(2018, 1, 1), Active())
    model.set_session(event)
    assert model.get_session_state() == Active()


def test_get_session_state_inactive(model):
    event = Event(datetime(2018, 1, 1), Inactive())
    model.set_session(event)
    assert model.get_session_state() == Inactive()


def test_get_desk_state_empty(model):
    assert model.get_desk_state() == Down()


def test_get_desk_state_up(model):
    event = Event(datetime(2018, 1, 1), Active())
    model.set_desk(event)
    assert model.get_desk_state() == Up()


def test_get_desk_state_down(model):
    event = Event(datetime(2018, 1, 1), Inactive())
    model.set_desk(event)
    assert model.get_desk_state() == Down()


def test_get_active_time_empty(model):
    assert model.get_active_time(datetime.min, datetime.max) is None


def test_get_active_time_active_zero(model):
    event = Event(datetime(2018, 1, 1), Active())
    model.set_session(event)
    assert model.get_active_time(datetime.min, event.index) == timedelta(0)


def test_get_active_time_active_10_minutes(model):
    a = datetime(2018, 1, 1, 0, 0, 0)
    b = datetime(2018, 1, 1, 0, 10, 0)
    model.set_session(Event(a, Active()))
    assert model.get_active_time(datetime.min, b) == timedelta(minutes=10)
