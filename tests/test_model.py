from autodesk.model import Database, Up, Down, Active, Inactive
from autodesk.spans import Event, Span
from contextlib import closing
from datetime import datetime, timedelta
import autodesk.model as model
import pytest
import tempfile


@pytest.fixture
def database():
    with tempfile.NamedTemporaryFile() as database_file:
        with closing(Database(database_file.name)) as database:
            yield database


def test_down_next():
    assert Down().next() == Up()


def test_down_test():
    assert Down().test(0, 1) == 0


def test_up_next():
    assert Up().next() == Down()


def test_up_test():
    assert Up().test(0, 1) == 1


def test_session_from_int():
    assert model.session_from_int(0) == Inactive()
    assert model.session_from_int(1) == Active()
    with pytest.raises(ValueError):
        model.session_from_int(2)


def test_desk_from_int():
    assert model.desk_from_int(0) == Down()
    assert model.desk_from_int(1) == Up()
    with pytest.raises(ValueError):
        model.desk_from_int(2)


def test_database_empty_events(database):
    assert database.get_desk_events() == []
    assert database.get_session_events() == []


def test_database_empty_spans(database):
    a = datetime.fromtimestamp(0)
    b = datetime.fromtimestamp(1)
    assert list(database.get_desk_spans(a, b)) == [Span(a, b, Down())]
    assert list(database.get_session_spans(a, b)) == [Span(a, b, Inactive())]


def test_database_insert_desk(database):
    a = datetime(2017, 1, 1)
    b = datetime(2017, 1, 2)
    c = datetime(2017, 1, 3)

    event = Event(b, Up())
    database.insert_desk_event(event)
    events = database.get_desk_events()
    assert events == [event]

    spans = list(database.get_desk_spans(a, c))
    assert spans == [Span(a, b, Down()), Span(b, c, Up())]


def test_database_insert_session(database):
    a = datetime(2017, 1, 1)
    b = datetime(2017, 1, 2)
    c = datetime(2017, 1, 3)

    event = Event(b, Active())
    database.insert_session_event(event)
    events = database.get_session_events()
    assert events == [event]

    spans = list(database.get_session_spans(a, c))
    assert spans == [Span(a, b, Inactive()), Span(b, c, Active())]


def test_snapshot_empty(database):
    a = datetime(2017, 1, 1)
    b = datetime(2017, 1, 2)
    snapshot = database.get_snapshot(a, b)
    assert snapshot.desk_spans == [Span(a, b, Down())]
    assert snapshot.desk_latest == Span(a, b, Down())
    assert snapshot.session_spans == [Span(a, b, Inactive())]
    assert snapshot.session_latest == Span(a, b, Inactive())
    assert snapshot.get_active_time() == timedelta(0)
    assert snapshot.get_latest_session_spans() == [Span(a, b, Inactive())]


def test_snapshot_example(database):
    a = datetime(2017, 1, 1, 0, 0, 0)
    b = datetime(2017, 1, 1, 0, 10, 0)
    c = datetime(2017, 1, 1, 0, 20, 0)
    d = datetime(2017, 1, 1, 0, 30, 0)
    e = datetime(2017, 1, 1, 0, 40, 0)
    session_events = [Event(b, Active()), Event(d, Inactive())]
    desk_events = [Event(c, Up())]
    for event in session_events:
        database.insert_session_event(event)
    for event in desk_events:
        database.insert_desk_event(event)
    snapshot = database.get_snapshot(a, e)
    assert snapshot.desk_spans == [Span(a, c, Down()), Span(c, e, Up())]
    assert snapshot.desk_latest == Span(c, e, Up())
    session_spans = [
        Span(a, b, Inactive()),
        Span(b, d, Active()),
        Span(d, e, Inactive())]
    assert snapshot.session_spans == session_spans
    assert snapshot.session_latest == Span(d, e, Inactive())
    assert snapshot.get_active_time() == timedelta(minutes=10)
    latest_session_spans = [Span(c, d, Active()), Span(d, e, Inactive())]
    assert snapshot.get_latest_session_spans() == latest_session_spans
