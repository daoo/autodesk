from autodesk.states import INACTIVE, ACTIVE, DOWN
from datetime import timedelta
import autodesk.spans as spans
import numpy as np
import pandas as pd


def enumerate_hours(t1, t2):
    t = t1
    while t < t2:
        yield (t.weekday(), t.hour)
        t = t + timedelta(hours=1)


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
        return list(spans.collect(
            default_data=DOWN,
            initial=initial,
            final=final,
            events=self.datastore.get_desk_events()))

    def get_session_spans(self, initial, final):
        return list(spans.collect(
            default_data=INACTIVE,
            initial=initial,
            final=final,
            events=self.datastore.get_session_events()))

    def get_session_state(self):
        events = self.datastore.get_session_events()
        return events[-1].data if events else INACTIVE

    def get_desk_state(self):
        events = self.datastore.get_desk_events()
        return events[-1].data if events else DOWN

    def get_active_time(self, initial, final):
        session_spans = self.get_session_spans(initial, final)
        if session_spans[-1].data == INACTIVE:
            return timedelta(0)

        desk_spans = self.get_desk_spans(initial, final)
        active_spans = spans.cut(
            desk_spans[-1].start,
            desk_spans[-1].end,
            session_spans)

        return spans.count(active_spans, ACTIVE, timedelta(0))

    def compute_hourly_relative_frequency(self, initial, final):
        spans = self.get_session_spans(initial, final)

        def to_tuple(span):
            return (span.start, span.end, span.data)
        df = pd.DataFrame(
            [to_tuple(span) for span in spans],
            columns=['start', 'end', 'state'])

        buckets = np.zeros((7, 24))
        for span in df[df.state == ACTIVE].itertuples():
            for (day, hour) in enumerate_hours(span.start, span.end):
                buckets[day, hour] += 1

        columns = [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday'
        ]
        return pd.DataFrame(buckets.T, columns=columns)
