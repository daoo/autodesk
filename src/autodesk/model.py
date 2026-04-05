from collections.abc import Generator, Sequence

from pandas import Timedelta, Timestamp

from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.states import ACTIVE, DOWN, INACTIVE, Desk, Session

type EventRow[S] = tuple[Timestamp, S]
type SpanRow[S] = tuple[Timestamp, Timestamp, S]
type HourlyCount = tuple[str, int, int]

WEEKDAYS: tuple[str, ...] = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def enumerate_hours(
    start: Timestamp,
    end: Timestamp,
) -> Generator[tuple[int, int], None, None]:
    time = start
    while time < end:
        yield (time.weekday(), time.hour)
        time = time + Timedelta(hours=1)


def collect[S: Desk | Session](
    default_state: S,
    initial: Timestamp,
    final: Timestamp,
    events: Sequence[EventRow[S]],
) -> Generator[SpanRow[S], None, None]:
    assert initial < final
    start = initial
    state = default_state
    for event_timestamp, event_state in events:
        assert start <= event_timestamp
        if state == event_state:
            # aggregate consecutive events with same state
            continue
        if start != event_timestamp:
            # do not emit zero-length spans
            yield (start, event_timestamp, state)
        start = event_timestamp
        state = event_state
    yield (start, final, state)


def cut[S: Desk | Session](
    start: Timestamp,
    end: Timestamp,
    spans: Sequence[SpanRow[S]],
) -> Generator[SpanRow[S], None, None]:
    for span_start, span_end, span_state in spans:
        if span_end >= start and span_start <= end:
            yield (
                start if span_start < start else span_start,
                end if span_end > end else span_end,
                span_state,
            )


class Model:
    def __init__(self, datastore: SqliteDataStore):
        self.datastore = datastore

    def close(self) -> None:
        self.datastore.close()

    def set_desk(self, timestamp: Timestamp, state: Desk) -> None:
        self.datastore.set_desk(timestamp, state)

    def set_session(self, timestamp: Timestamp, state: Session) -> None:
        self.datastore.set_session(timestamp, state)

    def get_desk_spans(
        self,
        initial: Timestamp,
        final: Timestamp,
    ) -> list[SpanRow[Desk]]:
        return list(
            collect(
                default_state=DOWN,
                initial=initial,
                final=final,
                events=self.datastore.get_desk_events(),
            ),
        )

    def get_session_spans(
        self,
        initial: Timestamp,
        final: Timestamp,
    ) -> list[SpanRow[Session]]:
        return list(
            collect(
                default_state=INACTIVE,
                initial=initial,
                final=final,
                events=self.datastore.get_session_events(),
            ),
        )

    def get_session_state(self) -> Session:
        events = self.datastore.get_session_events()
        return events[-1][1] if events else INACTIVE

    def get_desk_state(self) -> Desk:
        events = self.datastore.get_desk_events()
        return events[-1][1] if events else DOWN

    def get_active_time(self, initial: Timestamp, final: Timestamp) -> Timedelta:
        session_spans = self.get_session_spans(initial, final)
        if session_spans[-1][2] == INACTIVE:
            # TODO: Should return active time for current desk span
            return Timedelta(0)

        desk_spans = self.get_desk_spans(initial, final)
        current_spans = list(
            cut(
                desk_spans[-1][0],
                desk_spans[-1][1],
                session_spans,
            ),
        )

        active_time = Timedelta(0)
        for start, end, session_state in current_spans:
            if session_state == ACTIVE:
                active_time = active_time + (end - start)
        return active_time

    def compute_hourly_count(
        self,
        initial: Timestamp,
        final: Timestamp,
    ) -> list[HourlyCount]:
        spans = self.get_session_spans(initial, final)

        counts = [0] * (7 * 24)
        for span_start, span_end, session_state in spans:
            if session_state != ACTIVE:
                continue
            for day, hour in enumerate_hours(span_start, span_end):
                counts[day * 24 + hour] += 1

        rows: list[HourlyCount] = []
        for weekday_index, weekday in enumerate(WEEKDAYS):
            for hour in range(24):
                rows.append((weekday, hour, counts[weekday_index * 24 + hour]))
        return rows
