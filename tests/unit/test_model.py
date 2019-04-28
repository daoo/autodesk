from autodesk.model import Model
from autodesk.spans import Event, Span
from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.states import UP, DOWN, ACTIVE, INACTIVE
from datetime import datetime, timedelta
from tests.utils import StubDataStore
import pytest


@pytest.fixture()
def inmemory_model():
    model = Model(SqliteDataStore(':memory:'))
    yield model
    model.close()


def test_get_desk_spans_empty():
    t1 = datetime.min
    t2 = datetime.max
    model = Model(StubDataStore.empty())

    result = model.get_desk_spans(t1, t2)

    expected = [Span(t1, t2, DOWN)]
    assert result == expected


def test_get_session_spans_empty():
    t1 = datetime.min
    t2 = datetime.max
    model = Model(StubDataStore.empty())

    result = model.get_session_spans(t1, t2)

    expected = [Span(t1, t2, INACTIVE)]
    assert result == expected


def test_get_desk_spans_one_up_span():
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)
    t3 = datetime(2018, 1, 3)
    model = Model(StubDataStore(
        session_events=[],
        desk_events=[Event(t2, UP)]
    ))

    result = model.get_desk_spans(t1, t3)

    expected = [Span(t1, t2, DOWN), Span(t2, t3, UP)]
    assert result == expected


def test_get_session_spans_one_active_span():
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)
    t3 = datetime(2018, 1, 3)
    model = Model(StubDataStore(
        session_events=[Event(t2, ACTIVE)],
        desk_events=[]
    ))

    result = model.get_session_spans(t1, t3)

    expected = [Span(t1, t2, INACTIVE), Span(t2, t3, ACTIVE)]
    assert result == expected


def test_get_session_state_empty():
    model = Model(StubDataStore.empty())
    assert model.get_session_state() == INACTIVE


def test_get_desk_state_empty():
    model = Model(StubDataStore.empty())
    assert model.get_desk_state() == DOWN


def test_get_active_time_empty():
    model = Model(StubDataStore.empty())
    assert model.get_active_time(datetime.min, datetime.max) == timedelta(0)


def test_get_active_time_active_zero():
    t = datetime(2018, 1, 1)
    model = Model(StubDataStore(
        session_events=[Event(t, ACTIVE)],
        desk_events=[]
    ))
    assert model.get_active_time(datetime.min, t) == timedelta(0)


def test_get_active_time_active_10_minutes():
    t1 = datetime(2018, 1, 1, 0, 0, 0)
    t2 = datetime(2018, 1, 1, 0, 10, 0)
    model = Model(StubDataStore(
        session_events=[Event(t1, ACTIVE)],
        desk_events=[]
    ))
    assert model.get_active_time(datetime.min, t2) == timedelta(minutes=10)


def test_get_active_time_active_20_minutes_with_changed_desk_state():
    t1 = datetime(2018, 1, 1, 0, 0, 0)
    t2 = datetime(2018, 1, 1, 0, 10, 0)
    t3 = datetime(2018, 1, 1, 0, 20, 0)
    model = Model(StubDataStore(
        session_events=[Event(t1, ACTIVE)],
        desk_events=[Event(t2, UP)]
    ))
    assert model.get_active_time(datetime.min, t3) == timedelta(minutes=10)


def test_compute_hourly_relative_frequency_active_30_minutes():
    t1 = datetime(2017, 4, 12, 10, 0, 0)
    t2 = datetime(2017, 4, 12, 10, 30, 0)
    model = Model(StubDataStore(
        session_events=[Event(t1, ACTIVE), Event(t2, INACTIVE)],
        desk_events=[]
    ))
    result = model.compute_hourly_relative_frequency(t1, t2)
    assert result['Wednesday'][10] == 1


def test_compute_hourly_relative_frequency_active_0_minutes():
    t1 = datetime(2017, 4, 12, 10, 0, 0)
    t2 = datetime(2017, 4, 12, 10, 30, 0)
    model = Model(StubDataStore(
        session_events=[Event(t1, INACTIVE)],
        desk_events=[]
    ))
    result = model.compute_hourly_relative_frequency(t1, t2)
    assert result.values.sum() == 0


def test_set_session_state_active(inmemory_model):
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)

    inmemory_model.set_session(t1, ACTIVE)

    expected = [Span(t1, t2, ACTIVE)]
    assert inmemory_model.get_session_state() == ACTIVE
    assert inmemory_model.get_session_spans(t1, t2) == expected


def test_set_session_state_inactive(inmemory_model):
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)

    inmemory_model.set_session(t1, INACTIVE)

    expected = [Span(t1, t2, INACTIVE)]
    assert inmemory_model.get_session_state() == INACTIVE
    assert inmemory_model.get_session_spans(t1, t2) == expected


def test_set_desk_state_up(inmemory_model):
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)

    inmemory_model.set_desk(t1, UP)

    expected = [Span(t1, t2, UP)]
    assert inmemory_model.get_desk_state() == UP
    assert inmemory_model.get_desk_spans(t1, t2) == expected


def test_set_desk_state_down(inmemory_model):
    t1 = datetime(2018, 1, 1)
    t2 = datetime(2018, 1, 2)

    inmemory_model.set_desk(t1, DOWN)

    expected = [Span(t1, t2, DOWN)]
    assert inmemory_model.get_desk_state() == DOWN
    assert inmemory_model.get_desk_spans(t1, t2) == expected
