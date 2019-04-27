from autodesk.model import Model, Sqlite3DataStore, Up, Down, Active, Inactive
from autodesk.model import session_from_int, desk_from_int, event_from_row
from autodesk.spans import Event, Span
from datetime import datetime, timedelta
from tests.utils import StubDataStore
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
    model = Model(Sqlite3DataStore(':memory:'))
    yield model
    model.close()


def test_get_desk_spans_empty():
    t1 = datetime.min
    t2 = datetime.max
    model = Model(StubDataStore.empty())

    result = model.get_desk_spans(t1, t2)

    expected = [Span(t1, t2, Down())]
    assert result == expected


def test_get_session_spans_empty():
    t1 = datetime.min
    t2 = datetime.max
    model = Model(StubDataStore.empty())

    result = model.get_session_spans(t1, t2)

    expected = [Span(t1, t2, Inactive())]
    assert result == expected


def test_get_desk_spans_one_up_span():
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)
    t3 = datetime(2018, 1, 3)
    model = Model(StubDataStore(
        session_events=[],
        desk_events=[Event(t2, Up())]
    ))

    result = model.get_desk_spans(t1, t3)

    expected = [Span(t1, t2, Down()), Span(t2, t3, Up())]
    assert result == expected


def test_get_session_spans_one_active_span():
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)
    t3 = datetime(2018, 1, 3)
    model = Model(StubDataStore(
        session_events=[Event(t2, Active())],
        desk_events=[]
    ))

    result = model.get_session_spans(t1, t3)

    expected = [Span(t1, t2, Inactive()), Span(t2, t3, Active())]
    assert result == expected


def test_get_session_state_empty():
    model = Model(StubDataStore.empty())
    assert model.get_session_state() == Inactive()


def test_get_desk_state_empty():
    model = Model(StubDataStore.empty())
    assert model.get_desk_state() == Down()


def test_get_active_time_empty():
    model = Model(StubDataStore.empty())
    assert model.get_active_time(datetime.min, datetime.max) == timedelta(0)


def test_get_active_time_active_zero():
    t = datetime(2018, 1, 1)
    model = Model(StubDataStore(
        session_events=[Event(t, Active())],
        desk_events=[]
    ))
    assert model.get_active_time(datetime.min, t) == timedelta(0)


def test_get_active_time_active_10_minutes():
    t1 = datetime(2018, 1, 1, 0, 0, 0)
    t2 = datetime(2018, 1, 1, 0, 10, 0)
    model = Model(StubDataStore(
        session_events=[Event(t1, Active())],
        desk_events=[]
    ))
    assert model.get_active_time(datetime.min, t2) == timedelta(minutes=10)


def test_get_active_time_active_20_minutes_with_changed_desk_state():
    t1 = datetime(2018, 1, 1, 0, 0, 0)
    t2 = datetime(2018, 1, 1, 0, 10, 0)
    t3 = datetime(2018, 1, 1, 0, 20, 0)
    model = Model(StubDataStore(
        session_events=[Event(t1, Active())],
        desk_events=[Event(t2, Up())]
    ))
    assert model.get_active_time(datetime.min, t3) == timedelta(minutes=10)


def test_compute_hourly_relative_frequency_active_30_minutes():
    t1 = datetime(2017, 4, 12, 10, 0, 0)
    t2 = datetime(2017, 4, 12, 10, 30, 0)
    model = Model(StubDataStore(
        session_events=[Event(t1, Active()), Event(t2, Inactive())],
        desk_events=[]
    ))
    result = model.compute_hourly_relative_frequency(t1, t2)
    assert result['Wednesday'][10] == 1


def test_compute_hourly_relative_frequency_active_0_minutes():
    t1 = datetime(2017, 4, 12, 10, 0, 0)
    t2 = datetime(2017, 4, 12, 10, 30, 0)
    model = Model(StubDataStore(
        session_events=[Event(t1, Inactive())],
        desk_events=[]
    ))
    result = model.compute_hourly_relative_frequency(t1, t2)
    assert result.values.sum() == 0


def test_set_session_state_active(inmemory_model):
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)

    inmemory_model.set_session(Event(t1, Active()))

    expected = [Span(t1, t2, Active())]
    assert inmemory_model.get_session_state() == Active()
    assert inmemory_model.get_session_spans(t1, t2) == expected


def test_set_session_state_inactive(inmemory_model):
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)

    inmemory_model.set_session(Event(t1, Inactive()))

    expected = [Span(t1, t2, Inactive())]
    assert inmemory_model.get_session_state() == Inactive()
    assert inmemory_model.get_session_spans(t1, t2) == expected


def test_set_desk_state_up(inmemory_model):
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)

    inmemory_model.set_desk(Event(t1, Up()))

    expected = [Span(t1, t2, Up())]
    assert inmemory_model.get_desk_state() == Up()
    assert inmemory_model.get_desk_spans(t1, t2) == expected


def test_set_desk_state_down(inmemory_model):
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)

    inmemory_model.set_desk(Event(t1, Down()))

    expected = [Span(t1, t2, Down())]
    assert inmemory_model.get_desk_state() == Down()
    assert inmemory_model.get_desk_spans(t1, t2) == expected
