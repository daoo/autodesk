from collections.abc import Generator
from typing import Any

import numpy as np
import pandas as pd
from pandas import Timedelta, Timestamp

from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.states import ACTIVE, DOWN, INACTIVE, Desk, Session


def enumerate_hours(start, end) -> Generator[tuple[int, int], None, None]:
    time = start
    while time < end:
        yield (time.weekday(), time.hour)
        time = time + Timedelta(hours=1)


def collect(
    default_state: Any,
    initial: Timestamp,
    final: Timestamp,
    events: pd.DataFrame,
) -> Generator[tuple[Any, Any, Any], None, None]:
    assert initial < final
    start = initial
    state = default_state
    for event in events.itertuples():
        assert start <= event.timestamp  # type: ignore
        if state == event.state:
            # aggregate consecutive events with same state
            continue
        if start != event.timestamp:
            # do not emit zero-length spans
            yield (start, event.timestamp, state)
        start = event.timestamp
        state = event.state
    yield (start, final, state)


def cut(start, end, spans):
    for span in spans.itertuples():
        if span.end >= start and span.start <= end:
            yield (
                start if span.start < start else span.start,
                end if span.end > end else span.end,
                span.state,
            )


class Model:
    def __init__(self, datastore: SqliteDataStore):
        self.datastore = datastore

    def close(self):
        self.datastore.close()

    def set_desk(self, timestamp: Timestamp, state: Desk):
        self.datastore.set_desk(timestamp, state)

    def set_session(self, timestamp: Timestamp, state: Session):
        self.datastore.set_session(timestamp, state)

    def get_desk_spans(self, initial: Timestamp, final: Timestamp):
        spans = collect(
            default_state=DOWN,
            initial=initial,
            final=final,
            events=self.datastore.get_desk_events(),
        )
        return pd.DataFrame.from_records(spans, columns=["start", "end", "state"])

    def get_session_spans(self, initial: Timestamp, final: Timestamp):
        spans = collect(
            default_state=INACTIVE,
            initial=initial,
            final=final,
            events=self.datastore.get_session_events(),
        )
        return pd.DataFrame.from_records(spans, columns=["start", "end", "state"])

    def get_session_state(self) -> Session:
        events = self.datastore.get_session_events()
        return events.iloc[-1].state if not events.empty else INACTIVE

    def get_desk_state(self) -> Desk:
        events = self.datastore.get_desk_events()
        return events.iloc[-1].state if not events.empty else DOWN

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
        return (active_spans.end - active_spans.start).sum()

    def compute_hourly_count(self, initial: Timestamp, final: Timestamp):
        spans = self.get_session_spans(initial, final)

        rows = np.zeros(7 * 24)
        for span in spans[spans.state == ACTIVE].itertuples():
            for day, hour in enumerate_hours(span.start, span.end):
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
            }
        )
