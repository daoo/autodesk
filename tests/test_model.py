from autodesk.spans import Event, Span
from contextlib import closing
from datetime import datetime, timedelta
import autodesk.model as model
import pytest
import tempfile


@pytest.fixture
def database():
    with tempfile.NamedTemporaryFile() as database_file:
        with closing(model.Database(database_file.name)) as database:
            yield database


def test_database_empty_events(database):
    assert database.get_desk_events() == []
    assert database.get_session_events() == []


def test_database_empty_spans(database):
    a = datetime.fromtimestamp(0)
    b = datetime.fromtimestamp(1)
    assert list(database.get_desk_spans(a, b)) == [Span(a, b, 0)]
    assert list(database.get_session_spans(a, b)) == [Span(a, b, 0)]


def test_database_insert_desk(database):
    a = datetime(2017, 1, 1)
    b = datetime(2017, 1, 2)
    c = datetime(2017, 1, 3)

    event = Event(b, 1)
    database.insert_desk_event(event)
    events = database.get_desk_events()
    assert events == [event]

    spans = list(database.get_desk_spans(a, c))
    assert spans == [Span(a, b, 0), Span(b, c, 1)]


def test_database_insert_session(database):
    a = datetime(2017, 1, 1)
    b = datetime(2017, 1, 2)
    c = datetime(2017, 1, 3)

    event = Event(b, 1)
    database.insert_session_event(event)
    events = database.get_session_events()
    assert events == [event]

    spans = list(database.get_session_spans(a, c))
    assert spans == [Span(a, b, 0), Span(b, c, 1)]


def test_snapshot_empty(database):
    a = datetime(2017, 1, 1)
    b = datetime(2017, 1, 2)
    snapshot = database.get_snapshot(a, b)
    assert snapshot.desk_spans == [Span(a, b, 0)]
    assert snapshot.desk_latest == Span(a, b, 0)
    assert snapshot.session_spans == [Span(a, b, 0)]
    assert snapshot.session_latest == Span(a, b, 0)
    assert snapshot.get_active_time() == timedelta(0)
    assert snapshot.get_latest_session_spans() == [Span(a, b, 0)]
    assert snapshot.get_next_state() == (model.LIMIT_DOWN, model.STATE_UP)


def test_snapshot_example(database):
    a = datetime(2017, 1, 1, 0, 0, 0)
    b = datetime(2017, 1, 1, 0, 10, 0)
    c = datetime(2017, 1, 1, 0, 20, 0)
    d = datetime(2017, 1, 1, 0, 30, 0)
    e = datetime(2017, 1, 1, 0, 40, 0)
    session_events = [Event(b, 1), Event(d, 0)]
    desk_events = [Event(c, 1)]
    for event in session_events:
        database.insert_session_event(event)
    for event in desk_events:
        database.insert_desk_event(event)
    snapshot = database.get_snapshot(a, e)
    assert snapshot.desk_spans == [Span(a, c, 0), Span(c, e, 1)]
    assert snapshot.desk_latest == Span(c, e, 1)
    assert snapshot.session_spans == [Span(a, b, 0), Span(b, d, 1), Span(d, e, 0)]
    assert snapshot.session_latest == Span(d, e, 0)
    assert snapshot.get_active_time() == timedelta(minutes=10)
    assert snapshot.get_latest_session_spans() == [Span(c, d, 1), Span(d, e, 0)]
    assert snapshot.get_next_state() == (timedelta(minutes=0), model.STATE_DOWN)
