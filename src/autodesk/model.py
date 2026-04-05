from collections.abc import Generator, Sequence
from datetime import datetime, timedelta

from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.states import ACTIVE, DOWN, INACTIVE, Desk, Session

type EventRow[S] = tuple[datetime, S]
type SpanRow[S] = tuple[datetime, datetime, S]
type HourlyCount = tuple[str, int, int]
ONE_HOUR = timedelta(hours=1)

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
    start: datetime,
    end: datetime,
) -> Generator[tuple[int, int], None, None]:
    time = start
    while time < end:
        yield (time.weekday(), time.hour)
        time = time + ONE_HOUR


def build_spans[S: Desk | Session](
    default_state: S,
    initial: datetime,
    final: datetime,
    events: Sequence[EventRow[S]],
) -> Generator[SpanRow[S], None, None]:
    if initial >= final:
        raise ValueError("expected initial < final")
    start = initial
    state = default_state
    for event_timestamp, event_state in events:
        if event_timestamp < start:
            raise ValueError("events must be monotonic and >= initial")
        if event_timestamp > final:
            raise ValueError("events must be <= final")
        if state == event_state:
            # aggregate consecutive events with same state
            continue
        if start != event_timestamp:
            # do not emit zero-length spans
            yield (start, event_timestamp, state)
        start = event_timestamp
        state = event_state
    if start != final:
        yield (start, final, state)


class Model:
    def __init__(self, datastore: SqliteDataStore):
        self.datastore = datastore

    def close(self) -> None:
        self.datastore.close()

    def set_desk(self, timestamp: datetime, state: Desk) -> None:
        self.datastore.set_desk(timestamp, state)

    def set_session(self, timestamp: datetime, state: Session) -> None:
        self.datastore.set_session(timestamp, state)

    def get_session_state(self) -> Session:
        event = self.datastore.get_last_session_event()
        return event[1] if event else INACTIVE

    def get_desk_state(self) -> Desk:
        event = self.datastore.get_last_desk_event()
        return event[1] if event else DOWN

    def _session_state_at(self, at: datetime) -> Session:
        event = self.datastore.get_last_session_event_before(at)
        return event[1] if event else INACTIVE

    def _desk_state_at(self, at: datetime) -> Desk:
        event = self.datastore.get_last_desk_event_before(at)
        return event[1] if event else DOWN

    def get_active_time(self, initial: datetime, final: datetime) -> timedelta:
        # Active time is measured only within the current desk span at `final`.
        if self._session_state_at(final) == INACTIVE:
            return timedelta(0)

        current_desk_span_start = initial
        desk_state = self._desk_state_at(initial)
        for event_timestamp, event_state in self.datastore.get_desk_events_between(
            initial,
            final,
        ):
            if desk_state == event_state:
                continue
            current_desk_span_start = event_timestamp
            desk_state = event_state

        active_time = timedelta(0)
        for start, end, session_state in build_spans(
            default_state=self._session_state_at(initial),
            initial=initial,
            final=final,
            events=self.datastore.get_session_events_between(initial, final),
        ):
            if session_state == ACTIVE:
                overlap_start = (
                    start
                    if start > current_desk_span_start
                    else current_desk_span_start
                )
                overlap_end = end if end < final else final
                if overlap_start < overlap_end:
                    active_time = active_time + (overlap_end - overlap_start)
        return active_time

    def compute_hourly_count(
        self,
        initial: datetime,
        final: datetime,
    ) -> list[HourlyCount]:
        counts = [0] * (7 * 24)
        for span_start, span_end, session_state in build_spans(
            default_state=self._session_state_at(initial),
            initial=initial,
            final=final,
            events=self.datastore.get_session_events_between(initial, final),
        ):
            if session_state != ACTIVE:
                continue
            for day, hour in enumerate_hours(span_start, span_end):
                counts[day * 24 + hour] += 1

        rows: list[HourlyCount] = []
        for weekday_index, weekday in enumerate(WEEKDAYS):
            for hour in range(24):
                rows.append((weekday, hour, counts[weekday_index * 24 + hour]))
        return rows
