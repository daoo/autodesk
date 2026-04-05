from datetime import datetime, timedelta

import pytest

from autodesk.model import Model, build_spans
from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.states import ACTIVE, DOWN, INACTIVE, UP
from tests.stubdatastore import empty_data_store, fake_data_store


@pytest.fixture
def inmemory_model():
    model = Model(SqliteDataStore.open(":memory:"))
    yield model
    model.close()


def test_build_spans_aggregates_consecutive_identical_states():
    t1 = datetime(2018, 1, 1, 10, 0, 0)
    t2 = datetime(2018, 1, 1, 11, 0, 0)
    t3 = datetime(2018, 1, 1, 12, 0, 0)
    t4 = datetime(2018, 1, 1, 13, 0, 0)

    spans = list(
        build_spans(
            default_state=INACTIVE,
            initial=t1,
            final=t4,
            events=[(t2, ACTIVE), (t3, ACTIVE)],
        ),
    )

    assert spans == [(t1, t2, INACTIVE), (t2, t4, ACTIVE)]


def test_build_spans_skips_zero_length_transition_at_initial():
    t1 = datetime(2018, 1, 1, 10, 0, 0)
    t2 = datetime(2018, 1, 1, 11, 0, 0)

    spans = list(
        build_spans(
            default_state=INACTIVE,
            initial=t1,
            final=t2,
            events=[(t1, ACTIVE)],
        ),
    )

    assert spans == [(t1, t2, ACTIVE)]


def test_build_spans_invalid_time_range_raises_value_error():
    t = datetime(2018, 1, 1, 10, 0, 0)
    with pytest.raises(ValueError, match="expected initial < final"):
        list(
            build_spans(
                default_state=INACTIVE,
                initial=t,
                final=t,
                events=[],
            ),
        )


def test_build_spans_non_monotonic_events_raise_value_error():
    t1 = datetime(2018, 1, 1, 10, 0, 0)
    t2 = datetime(2018, 1, 1, 11, 0, 0)
    t3 = datetime(2018, 1, 1, 12, 0, 0)
    with pytest.raises(ValueError, match="events must be monotonic and >= initial"):
        list(
            build_spans(
                default_state=INACTIVE,
                initial=t1,
                final=t3,
                events=[(t2, ACTIVE), (t1, INACTIVE)],
            ),
        )


def test_build_spans_events_after_final_raise_value_error():
    t1 = datetime(2018, 1, 1, 10, 0, 0)
    t2 = datetime(2018, 1, 1, 11, 0, 0)
    t3 = datetime(2018, 1, 1, 12, 0, 0)
    with pytest.raises(ValueError, match="events must be <= final"):
        list(
            build_spans(
                default_state=INACTIVE,
                initial=t1,
                final=t2,
                events=[(t3, ACTIVE)],
            ),
        )


def test_build_spans_invariants_sorted_non_overlapping_non_zero_and_ends_at_final():
    t1 = datetime(2018, 1, 1, 10, 0, 0)
    t2 = datetime(2018, 1, 1, 11, 0, 0)
    t3 = datetime(2018, 1, 1, 12, 0, 0)
    t4 = datetime(2018, 1, 1, 13, 0, 0)
    spans = list(
        build_spans(
            default_state=INACTIVE,
            initial=t1,
            final=t4,
            events=[(t2, ACTIVE), (t3, INACTIVE)],
        ),
    )

    assert spans[-1][1] == t4
    for index, (start, end, _) in enumerate(spans):
        assert start < end
        if index > 0:
            previous_end = spans[index - 1][1]
            assert previous_end <= start


def test_get_session_state_empty(mocker):
    model = Model(empty_data_store(mocker))
    assert model.get_session_state() == INACTIVE


def test_get_desk_state_empty(mocker):
    model = Model(empty_data_store(mocker))
    assert model.get_desk_state() == DOWN


def test_get_active_time_empty(mocker):
    model = Model(empty_data_store(mocker))
    assert model.get_active_time(datetime.min, datetime.max) == timedelta(0)


def test_get_active_time_active_zero(mocker):
    t = datetime(2018, 1, 1)
    model = Model(fake_data_store(mocker, session_events=[(t, ACTIVE)], desk_events=[]))
    assert model.get_active_time(datetime.min, t) == timedelta(0)


def test_get_active_time_active_for_10_minutes(mocker):
    t1 = datetime(2018, 1, 1, 0, 0, 0)
    t2 = datetime(2018, 1, 1, 0, 10, 0)
    model = Model(
        fake_data_store(mocker, session_events=[(t1, ACTIVE)], desk_events=[]),
    )
    assert model.get_active_time(datetime.min, t2) == timedelta(minutes=10)


def test_get_active_time_just_after_desk_change(mocker):
    t1 = datetime(2018, 1, 1, 0, 0, 0)
    t2 = datetime(2018, 1, 1, 0, 10, 0)
    model = Model(
        fake_data_store(mocker, session_events=[(t1, ACTIVE)], desk_events=[(t2, UP)]),
    )
    assert model.get_active_time(datetime.min, t2) == timedelta(0)


def test_get_active_time_active_20_minutes_with_changed_desk_state(mocker):
    t1 = datetime(2018, 1, 1, 0, 0, 0)
    t2 = datetime(2018, 1, 1, 0, 10, 0)
    t3 = datetime(2018, 1, 1, 0, 20, 0)
    model = Model(
        fake_data_store(mocker, session_events=[(t1, ACTIVE)], desk_events=[(t2, UP)]),
    )
    assert model.get_active_time(datetime.min, t3) == timedelta(minutes=10)


def test_get_active_time_ignores_duplicate_desk_state_events(mocker):
    t1 = datetime(2018, 1, 1, 0, 0, 0)
    t2 = datetime(2018, 1, 1, 0, 10, 0)
    t3 = datetime(2018, 1, 1, 0, 20, 0)
    model = Model(
        fake_data_store(
            mocker,
            session_events=[(t1, ACTIVE)],
            desk_events=[(t2, UP), (t3, UP)],
        ),
    )

    assert model.get_active_time(datetime.min, t3) == timedelta(minutes=10)


def test_compute_hourly_count_active_30_minutes(mocker):
    t1 = datetime(2017, 4, 12, 10, 0, 0)
    t2 = datetime(2017, 4, 12, 10, 30, 0)
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
    t1 = datetime(2017, 4, 12, 10, 0, 0)
    t2 = datetime(2017, 4, 12, 10, 30, 0)
    model = Model(
        fake_data_store(mocker, session_events=[(t1, INACTIVE)], desk_events=[]),
    )
    result = model.compute_hourly_count(t1, t2)
    assert sum(counts for _, _, counts in result) == 0


def test_compute_hourly_count_active_multi_hour_increments_each_hour(mocker):
    t1 = datetime(2017, 4, 12, 10, 0, 0)
    t2 = datetime(2017, 4, 12, 12, 0, 0)
    model = Model(
        fake_data_store(
            mocker,
            session_events=[(t1, ACTIVE), (t2, INACTIVE)],
            desk_events=[],
        ),
    )

    result = model.compute_hourly_count(t1, t2)
    wednesday_counts = {
        hour: counts for weekday, hour, counts in result if weekday == "Wednesday"
    }
    assert wednesday_counts[10] == 1
    assert wednesday_counts[11] == 1
    assert wednesday_counts[12] == 0


def test_set_session_state_active(inmemory_model):
    t1 = datetime(2018, 1, 1)

    inmemory_model.set_session(t1, ACTIVE)

    assert inmemory_model.get_session_state() == ACTIVE
    assert inmemory_model.datastore.get_session_events_between(t1, t1) == [(t1, ACTIVE)]


def test_set_session_state_inactive(inmemory_model):
    t1 = datetime(2018, 1, 1)

    inmemory_model.set_session(t1, INACTIVE)

    assert inmemory_model.get_session_state() == INACTIVE
    assert inmemory_model.datastore.get_session_events_between(t1, t1) == [
        (t1, INACTIVE),
    ]


def test_set_desk_state_up(inmemory_model):
    t1 = datetime(2018, 1, 1)

    inmemory_model.set_desk(t1, UP)

    assert inmemory_model.get_desk_state() == UP
    assert inmemory_model.datastore.get_desk_events_between(t1, t1) == [(t1, UP)]


def test_set_desk_state_down(inmemory_model):
    t1 = datetime(2018, 1, 1)

    inmemory_model.set_desk(t1, DOWN)

    assert inmemory_model.get_desk_state() == DOWN
    assert inmemory_model.datastore.get_desk_events_between(t1, t1) == [(t1, DOWN)]
