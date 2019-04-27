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
def inmemory_model():
    model = Model(':memory:')
    yield model
    model.close()


def test_empty_spans(inmemory_model):
    a = datetime.min
    b = datetime.max
    assert inmemory_model.get_desk_spans(a, b) == [Span(a, b, Down())]
    assert inmemory_model.get_session_spans(a, b) == [Span(a, b, Inactive())]


def test_set_desk(inmemory_model):
    t1 = datetime(2017, 1, 1)
    t2 = datetime(2017, 1, 2)
    inmemory_model.set_desk(Event(t2, Up()))
    expected = [Span(t1, t2, Down()), Span(t2, t2, Up())]
    assert inmemory_model.get_desk_spans(t1, t2) == expected


def test_set_session(inmemory_model):
    t1 = datetime(2017, 1, 1)
    t2 = datetime(2017, 1, 2)
    inmemory_model.set_session(Event(t2, Active()))
    expected = [Span(t1, t2, Inactive()), Span(t2, t2, Active())]
    assert inmemory_model.get_session_spans(t1, t2) == expected


def test_get_desk_spans(inmemory_model):
    a = datetime(2018, 1, 1)
    b = datetime(2018, 1, 2)
    c = datetime(2018, 1, 3)
    inmemory_model.set_desk(Event(b, Up()))
    expected = [Span(a, b, Down()), Span(b, c, Up())]
    assert inmemory_model.get_desk_spans(a, c) == expected


def test_get_session_spans(inmemory_model):
    a = datetime(2018, 1, 1)
    b = datetime(2018, 1, 2)
    c = datetime(2018, 1, 3)
    inmemory_model.set_session(Event(b, Active()))
    expected = [Span(a, b, Inactive()), Span(b, c, Active())]
    assert inmemory_model.get_session_spans(a, c) == expected


def test_get_session_state_empty(inmemory_model):
    assert inmemory_model.get_session_state() == Inactive()


def test_get_session_state_active(inmemory_model):
    event = Event(datetime(2018, 1, 1), Active())
    inmemory_model.set_session(event)
    assert inmemory_model.get_session_state() == Active()


def test_get_session_state_inactive(inmemory_model):
    event = Event(datetime(2018, 1, 1), Inactive())
    inmemory_model.set_session(event)
    assert inmemory_model.get_session_state() == Inactive()


def test_get_desk_state_empty(inmemory_model):
    assert inmemory_model.get_desk_state() == Down()


def test_get_desk_state_up(inmemory_model):
    event = Event(datetime(2018, 1, 1), Active())
    inmemory_model.set_desk(event)
    assert inmemory_model.get_desk_state() == Up()


def test_get_desk_state_down(inmemory_model):
    event = Event(datetime(2018, 1, 1), Inactive())
    inmemory_model.set_desk(event)
    assert inmemory_model.get_desk_state() == Down()


def test_get_active_time_empty(inmemory_model):
    assert inmemory_model.get_active_time(datetime.min, datetime.max) is None


def test_get_active_time_active_zero(inmemory_model):
    event = Event(datetime(2018, 1, 1), Active())
    inmemory_model.set_session(event)
    result = inmemory_model.get_active_time(datetime.min, event.index)
    assert result == timedelta(0)


def test_get_active_time_active_10_minutes(inmemory_model):
    a = datetime(2018, 1, 1, 0, 0, 0)
    b = datetime(2018, 1, 1, 0, 10, 0)
    inmemory_model.set_session(Event(a, Active()))
    result = inmemory_model.get_active_time(datetime.min, b)
    assert result == timedelta(minutes=10)
