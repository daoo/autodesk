from contextlib import closing
from datetime import datetime, timedelta
import autodesk.spans as spans
import sqlite3

STATE_DOWN = 0
STATE_UP = 1
SESSION_INACTIVE = 0
SESSION_ACTIVE = 1
LIMIT_DOWN = timedelta(minutes=50)
LIMIT_UP = timedelta(minutes=10)


def event_from_row(_, values):
    return spans.Event(
        datetime.fromtimestamp(values[0]),
        values[1])


def get(db, query):
    with closing(db.execute(query)) as cursor:
        return cursor.fetchall()


class Database:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = event_from_row
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS session('
            'date INTEGER NOT NULL,'
            'data INTEGER NOT NULL)')
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS desk('
            'date INTEGER NOT NULL,'
            'data INTEGER NOT NULL)')

    def close(self):
        self.db.close()

    def insert_desk_event(self, event):
        self.db.execute('INSERT INTO desk values(?, ?)',
                        (event.index.timestamp(), event.data))
        self.db.commit()

    def insert_session_event(self, event):
        self.db.execute('INSERT INTO session values(?, ?)',
                        (event.index.timestamp(), event.data))
        self.db.commit()

    def get_desk_events(self):
        return get(self.db, 'SELECT * FROM desk ORDER BY date ASC')

    def get_session_events(self):
        return get(self.db, 'SELECT * FROM session ORDER BY date ASC')

    def get_desk_spans(self, initial, final):
        return spans.collect(
            default_data=0,
            initial=initial,
            final=final,
            events=self.get_desk_events())

    def get_session_spans(self, initial, final):
        return spans.collect(
            default_data=0,
            initial=initial,
            final=final,
            events=self.get_session_events())

    def get_snapshot(self, initial, final):
        return Snapshot(
            desk_spans=self.get_desk_spans(initial, final),
            session_spans=self.get_session_spans(initial, final))


class Snapshot:
    def __init__(self, desk_spans, session_spans):
        self.desk_spans = list(desk_spans)
        self.desk_latest = self.desk_spans[-1]

        self.session_spans = list(session_spans)
        self.session_latest = self.session_spans[-1]

    def get_latest_session_spans(self):
        return list(spans.cut(
            self.desk_latest.start,
            self.desk_latest.end,
            self.session_spans))

    def get_active_time(self):
        return spans.count(
            self.get_latest_session_spans(),
            SESSION_ACTIVE,
            timedelta(0))

    def get_next_state(self):
        active_time = self.get_active_time()
        if self.desk_latest.data == STATE_DOWN:
            limit = LIMIT_DOWN
            return (limit - active_time, STATE_UP)
        elif self.desk_latest.data == STATE_UP:
            limit = LIMIT_UP
            return (limit - active_time, STATE_DOWN)
        else:
            assert False

    def __repr__(self):
        return (
            'desk_spans:\n  {}\n'
            'desk_latest:\n  {}\n'
            'session_spans:\n  {}\n'
            'sessions_desk:\n  {}\n'
            'active_time:\n  {}\n'
        ).format(
            '\n  '.join(map(repr, self.desk_spans)),
            self.desk_latest,
            '\n  '.join(map(repr, self.session_spans)),
            '\n  '.join(map(repr, self.get_latest_session_spans())),
            self.get_active_time()
        )
