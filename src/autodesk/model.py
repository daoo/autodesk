from collections.abc import Generator
from typing import cast

import numpy as np
import pandas as pd
from pandas import Timedelta, Timestamp

from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.states import ACTIVE, DOWN, INACTIVE, Desk, Session

type SpanRow[S] = tuple[Timestamp, Timestamp, S]


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
    events: pd.DataFrame,
) -> Generator[SpanRow[S], None, None]:
    assert initial < final
    start = initial
    state = default_state
    for event in events.itertuples():
        event_timestamp = cast(Timestamp, event.timestamp)
        event_state = cast(S, event.state)
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
    spans: pd.DataFrame,
) -> Generator[SpanRow[S], None, None]:
    for span in spans.itertuples():
        span_start = cast(Timestamp, span.start)
        span_end = cast(Timestamp, span.end)
        span_state = cast(S, span.state)
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

    def get_desk_spans(self, initial: Timestamp, final: Timestamp) -> pd.DataFrame:
        spans = collect(
            default_state=DOWN,
            initial=initial,
            final=final,
            events=self.datastore.get_desk_events(),
        )
        return pd.DataFrame.from_records(spans, columns=["start", "end", "state"])

    def get_session_spans(self, initial: Timestamp, final: Timestamp) -> pd.DataFrame:
        spans = collect(
            default_state=INACTIVE,
            initial=initial,
            final=final,
            events=self.datastore.get_session_events(),
        )
        return pd.DataFrame.from_records(spans, columns=["start", "end", "state"])

    def get_session_state(self) -> Session:
        events = self.datastore.get_session_events()
        return cast(Session, events.iloc[-1].state) if not events.empty else INACTIVE

    def get_desk_state(self) -> Desk:
        events = self.datastore.get_desk_events()
        return cast(Desk, events.iloc[-1].state) if not events.empty else DOWN

    def get_active_time(self, initial: Timestamp, final: Timestamp) -> Timedelta:
        session_spans = self.get_session_spans(initial, final)
        if session_spans.iloc[-1].state == INACTIVE:
            # TODO: Should return active time for current desk span
            return Timedelta(0)

        desk_spans = self.get_desk_spans(initial, final)
        current_spans = pd.DataFrame.from_records(
            cut(desk_spans.iloc[-1].start, desk_spans.iloc[-1].end, session_spans),
            columns=["start", "end", "state"],
        )

        active_spans = current_spans[current_spans.state == ACTIVE]
        return cast(Timedelta, (active_spans.end - active_spans.start).sum())

    def compute_hourly_count(
        self,
        initial: Timestamp,
        final: Timestamp,
    ) -> pd.DataFrame:
        spans = self.get_session_spans(initial, final)

        rows = np.zeros(7 * 24)
        for span in spans[spans.state == ACTIVE].itertuples():
            span_start = cast(Timestamp, span.start)
            span_end = cast(Timestamp, span.end)
            for day, hour in enumerate_hours(span_start, span_end):
                rows[day * 24 + hour] += 1

        weekdays = pd.Series(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            dtype="string",
        )
        return pd.DataFrame(
            {
                "weekday": np.repeat(weekdays, 24),
                "hour": np.tile(np.arange(24), 7),
                "counts": rows,
            },
        )
