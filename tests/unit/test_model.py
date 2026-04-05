import pytest
from pandas import Timedelta, Timestamp

from autodesk.model import Model
from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.states import ACTIVE, DOWN, INACTIVE, UP
from tests.stubdatastore import empty_data_store, fake_data_store


@pytest.fixture
def inmemory_model():
    model = Model(SqliteDataStore.open(":memory:"))
    yield model
    model.close()


def test_get_desk_spans_empty(mocker):
    t1 = Timestamp.min
    t2 = Timestamp.max
    model = Model(empty_data_store(mocker))

    result = model.get_desk_spans(t1, t2)

    expected = [(t1, t2, DOWN)]
    assert result == expected


def test_get_session_spans_empty(mocker):
    t1 = Timestamp.min
    t2 = Timestamp.max
    model = Model(empty_data_store(mocker))

    result = model.get_session_spans(t1, t2)

    expected = [(t1, t2, INACTIVE)]
    assert result == expected


def test_get_desk_spans_one_up_span(mocker):
    t1 = Timestamp(2018, 1, 1)
    t2 = Timestamp(2018, 1, 2)
    t3 = Timestamp(2018, 1, 3)
    model = Model(fake_data_store(mocker, session_events=[], desk_events=[(t2, UP)]))

    result = model.get_desk_spans(t1, t3)

    expected = [(t1, t2, DOWN), (t2, t3, UP)]
    assert result == expected


def test_get_session_spans_one_active_span(mocker):
    t1 = Timestamp(2018, 1, 1)
    t2 = Timestamp(2018, 1, 2)
    t3 = Timestamp(2018, 1, 3)
    model = Model(
        fake_data_store(mocker, session_events=[(t2, ACTIVE)], desk_events=[]),
    )

    result = model.get_session_spans(t1, t3)

    expected = [(t1, t2, INACTIVE), (t2, t3, ACTIVE)]
    assert result == expected


def test_get_session_state_empty(mocker):
    model = Model(empty_data_store(mocker))
    assert model.get_session_state() == INACTIVE


def test_get_desk_state_empty(mocker):
    model = Model(empty_data_store(mocker))
    assert model.get_desk_state() == DOWN


def test_get_active_time_empty(mocker):
    model = Model(empty_data_store(mocker))
    assert model.get_active_time(Timestamp.min, Timestamp.max) == Timedelta(0)


def test_get_active_time_active_zero(mocker):
    t = Timestamp(2018, 1, 1)
    model = Model(fake_data_store(mocker, session_events=[(t, ACTIVE)], desk_events=[]))
    assert model.get_active_time(Timestamp.min, t) == Timedelta(0)


def test_get_active_time_active_for_10_minutes(mocker):
    t1 = Timestamp(2018, 1, 1, 0, 0, 0)
    t2 = Timestamp(2018, 1, 1, 0, 10, 0)
    model = Model(
        fake_data_store(mocker, session_events=[(t1, ACTIVE)], desk_events=[]),
    )
    assert model.get_active_time(Timestamp.min, t2) == Timedelta(minutes=10)


def test_get_active_time_just_after_desk_change(mocker):
    t1 = Timestamp(2018, 1, 1, 0, 0, 0)
    t2 = Timestamp(2018, 1, 1, 0, 10, 0)
    model = Model(
        fake_data_store(mocker, session_events=[(t1, ACTIVE)], desk_events=[(t2, UP)]),
    )
    assert model.get_active_time(Timestamp.min, t2) == Timedelta(0)


def test_get_active_time_active_20_minutes_with_changed_desk_state(mocker):
    t1 = Timestamp(2018, 1, 1, 0, 0, 0)
    t2 = Timestamp(2018, 1, 1, 0, 10, 0)
    t3 = Timestamp(2018, 1, 1, 0, 20, 0)
    model = Model(
        fake_data_store(mocker, session_events=[(t1, ACTIVE)], desk_events=[(t2, UP)]),
    )
    assert model.get_active_time(Timestamp.min, t3) == Timedelta(minutes=10)


def test_compute_hourly_count_active_30_minutes(mocker):
    t1 = Timestamp(2017, 4, 12, 10, 0, 0)
    t2 = Timestamp(2017, 4, 12, 10, 30, 0)
    model = Model(
        fake_data_store(
            mocker,
            session_events=[(t1, ACTIVE), (t2, INACTIVE)],
            desk_events=[],
        ),
    )
    result = model.compute_hourly_count(t1, t2)
    specific_hour = [
        counts
        for weekday, hour, counts in result
        if weekday == "Wednesday" and hour == 10
    ]
    assert specific_hour[0] == 1


def test_compute_hourly_count_active_0_minutes(mocker):
    t1 = Timestamp(2017, 4, 12, 10, 0, 0)
    t2 = Timestamp(2017, 4, 12, 10, 30, 0)
    model = Model(
        fake_data_store(mocker, session_events=[(t1, INACTIVE)], desk_events=[]),
    )
    result = model.compute_hourly_count(t1, t2)
    assert sum(counts for _, _, counts in result) == 0


def test_set_session_state_active(inmemory_model):
    t1 = Timestamp(2018, 1, 1)
    t2 = Timestamp(2018, 1, 2)

    inmemory_model.set_session(t1, ACTIVE)

    expected = [(t1, t2, ACTIVE)]
    assert inmemory_model.get_session_state() == ACTIVE
    assert inmemory_model.get_session_spans(t1, t2) == expected


def test_set_session_state_inactive(inmemory_model):
    t1 = Timestamp(2018, 1, 1)
    t2 = Timestamp(2018, 1, 2)

    inmemory_model.set_session(t1, INACTIVE)

    expected = [(t1, t2, INACTIVE)]
    assert inmemory_model.get_session_state() == INACTIVE
    assert inmemory_model.get_session_spans(t1, t2) == expected


def test_set_desk_state_up(inmemory_model):
    t1 = Timestamp(2018, 1, 1)
    t2 = Timestamp(2018, 1, 2)

    inmemory_model.set_desk(t1, UP)

    expected = [(t1, t2, UP)]
    assert inmemory_model.get_desk_state() == UP
    assert inmemory_model.get_desk_spans(t1, t2) == expected


def test_set_desk_state_down(inmemory_model):
    t1 = Timestamp(2018, 1, 1)
    t2 = Timestamp(2018, 1, 2)

    inmemory_model.set_desk(t1, DOWN)

    expected = [(t1, t2, DOWN)]
    assert inmemory_model.get_desk_state() == DOWN
    assert inmemory_model.get_desk_spans(t1, t2) == expected
