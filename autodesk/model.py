from autodesk.states import INACTIVE, ACTIVE, DOWN
from pandas import Timedelta
import numpy as np
import pandas as pd


def enumerate_hours(t1, t2):
    t = t1
    while t < t2:
        yield (t.weekday(), t.hour)
        t = t + Timedelta(hours=1)


def collect(default_state, initial, final, events):
    assert initial < final
    start = initial
    state = default_state
    for event in events.itertuples():
        assert start <= event.date
        if state == event.state:
            # aggregate consecutive events with same state
            continue
        if start != event.date:
            # do not emit zero-length spans
            yield (start, event.date, state)
        start = event.date
        state = event.state
    yield (start, final, state)


def cut(start, end, spans):
    for span in spans.itertuples():
        if span.end >= start and span.start <= end:
            a = start if span.start < start else span.start
            b = end if span.end > end else span.end
            yield (a, b, span.state)


class Model:
    def __init__(self, datastore):
        self.datastore = datastore

    def close(self):
        self.datastore.close()

    def set_desk(self, date, state):
        self.datastore.set_desk(date, state)

    def set_session(self, date, state):
        self.datastore.set_session(date, state)

    def get_desk_spans(self, initial, final):
        spans = collect(
            default_state=DOWN,
            initial=initial,
            final=final,
            events=self.datastore.get_desk_events())
        return pd.DataFrame.from_records(
            spans, columns=['start', 'end', 'state'])

    def get_session_spans(self, initial, final):
        spans = collect(
            default_state=INACTIVE,
            initial=initial,
            final=final,
            events=self.datastore.get_session_events())
        return pd.DataFrame.from_records(
            spans, columns=['start', 'end', 'state'])

    def get_session_state(self):
        events = self.datastore.get_session_events()
        return events.iloc[-1].state if not events.empty else INACTIVE

    def get_desk_state(self):
        events = self.datastore.get_desk_events()
        return events.iloc[-1].state if not events.empty else DOWN

    def get_active_time(self, initial, final):
        session_spans = self.get_session_spans(initial, final)
        if session_spans.iloc[-1].state == INACTIVE:
            # TODO: Should return active time for current desk span
            return Timedelta(0)

        desk_spans = self.get_desk_spans(initial, final)
        current_spans = pd.DataFrame.from_records(cut(
            desk_spans.iloc[-1].start,
            desk_spans.iloc[-1].end,
            session_spans), columns=['start', 'end', 'state'])

        active_spans = current_spans[current_spans.state == ACTIVE]
        return (active_spans.end - active_spans.start).sum()

    def compute_hourly_count(self, initial, final):
        spans = self.get_session_spans(initial, final)

        rows = np.zeros((7 * 24))
        for span in spans[spans.state == ACTIVE].itertuples():
            for (day, hour) in enumerate_hours(span.start, span.end):
                rows[day * 24 + hour] += 1

        weekdays = [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday'
        ]
        return pd.DataFrame({
            'weekday': np.repeat(weekdays, 24),
            'hour': np.tile(np.arange(24), 7),
            'counts': rows
        })
