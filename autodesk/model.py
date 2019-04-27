from contextlib import closing
from datetime import timedelta
import autodesk.spans as spans
import logging
import numpy as np
import pandas as pd
import sqlite3


class Up:
    def next(self):
        return Down()

    def test(self, a, b):
        return b

    def __eq__(self, other):
        return isinstance(other, Up)


class Down:
    def next(self):
        return Up()

    def test(self, a, b):
        return a

    def __eq__(self, other):
        return isinstance(other, Down)


class Active:
    def active(self):
        return True

    def test(self, a, b):
        return b

    def __eq__(self, other):
        return isinstance(other, Active)


class Inactive:
    def active(self):
        return False

    def test(self, a, b):
        return a

    def __eq__(self, other):
        return isinstance(other, Inactive)


def session_from_int(value):
    if value == 0:
        return Inactive()
    elif value == 1:
        return Active()
    else:
        raise ValueError('incorrect session state')


def desk_from_int(value):
    if value == 0:
        return Down()
    elif value == 1:
        return Up()
    else:
        raise ValueError('incorrect desk state')


def event_from_row(cursor, values):
    time = values[0]
    assert cursor.description[0][0] == 'date'
    col_name = cursor.description[1][0]
    if col_name == 'active':
        return spans.Event(time, session_from_int(values[1]))
    elif col_name == 'state':
        return spans.Event(time, desk_from_int(values[1]))
    else:
        raise ValueError('incorrect column names')


class Sqlite3DataStore:
    def __init__(self, path):
        self.logger = logging.getLogger('sqlite3')
        self.logger.info('Opening database %s', path)
        self.db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = event_from_row
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS session('
            'date TIMESTAMP NOT NULL,'
            'active INTEGER NOT NULL)')
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS desk('
            'date TIMESTAMP NOT NULL,'
            'state INTEGER NOT NULL)')

    def close(self):
        self.db.close()

    def _get(self, query):
        with closing(self.db.execute(query)) as cursor:
            return cursor.fetchall()

    def get_desk_events(self):
        return self._get('SELECT * FROM desk ORDER BY date ASC')

    def get_session_events(self):
        return self._get('SELECT * FROM session ORDER BY date ASC')

    def set_desk(self, event):
        self.logger.debug(
            'set desk %s %s',
            event.index,
            event.data.test('down', 'up'))
        self.db.execute('INSERT INTO desk values(?, ?)',
                        (event.index, event.data.test(0, 1)))
        self.db.commit()

    def set_session(self, event):
        self.logger.debug(
            'set session %s %s',
            event.index,
            event.data.test('inactive', 'active'))
        self.db.execute('INSERT INTO session values(?, ?)',
                        (event.index, event.data.test(0, 1)))
        self.db.commit()


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

    def set_desk(self, event):
        self.datastore.set_desk(event)

    def set_session(self, event):
        self.datastore.set_session(event)

    def get_desk_spans(self, initial, final):
        return list(spans.collect(
            default_data=Down(),
            initial=initial,
            final=final,
            events=self.datastore.get_desk_events()))

    def get_session_spans(self, initial, final):
        return list(spans.collect(
            default_data=Inactive(),
            initial=initial,
            final=final,
            events=self.datastore.get_session_events()))

    def get_session_state(self):
        events = self.datastore.get_session_events()
        return events[-1].data if events else Inactive()

    def get_desk_state(self):
        events = self.datastore.get_desk_events()
        return events[-1].data if events else Down()

    def get_active_time(self, initial, final):
        session_spans = self.get_session_spans(initial, final)
        if not session_spans[-1].data.active():
            return timedelta(0)

        desk_spans = self.get_desk_spans(initial, final)
        active_spans = spans.cut(
            desk_spans[-1].start,
            desk_spans[-1].end,
            session_spans)

        return spans.count(active_spans, Active(), timedelta(0))

    def compute_hourly_relative_frequency(self, initial, final):
        spans = self.get_session_spans(initial, final)

        def to_tuple(span):
            return (span.start, span.end, span.data.active())
        df = pd.DataFrame(
            [to_tuple(span) for span in spans],
            columns=['start', 'end', 'active'])

        buckets = np.zeros((7, 24))
        for span in df[df.active].itertuples():
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
