from contextlib import closing
from datetime import datetime, timedelta
import autodesk.spans as spans
import sqlite3


class Up:
    def next(self):
        return Down()

    def limit(self):
        return timedelta(minutes=10)

    def test(self, a, b):
        return b

    def integer(self):
        return 1

    def __str__(self):
        return '1'

    def __eq__(self, other):
        return isinstance(other, Up)


class Down:
    def next(self):
        return Up()

    def limit(self):
        return timedelta(minutes=50)

    def test(self, a, b):
        return a

    def integer(self):
        return 0

    def __str__(self):
        return '0'

    def __eq__(self, other):
        return isinstance(other, Down)


class Active:
    def active(self):
        return True

    def integer(self):
        return 1

    def __str__(self):
        return '1'

    def __eq__(self, other):
        return isinstance(other, Active)


class Inactive:
    def active(self):
        return False

    def integer(self):
        return 0

    def __str__(self):
        return '0'

    def __eq__(self, other):
        return isinstance(other, Inactive)


def session_from_int(value):
    if value == 0:
        return Inactive()
    elif value == 1:
        return Active()
    else:
        raise ValueError()


def desk_from_int(value):
    if value == 0:
        return Down()
    elif value == 1:
        return Up()
    else:
        raise ValueError()


def event_from_row(cursor, values):
    time = datetime.fromtimestamp(values[0])
    assert cursor.description[0][0] == 'date'
    col_name = cursor.description[1][0]
    state = None
    try:
        if col_name == 'active':
            state = session_from_int(values[1])
        elif col_name == 'state':
            state = desk_from_int(values[1])
        else:
            assert False
    except:
        assert False

    return spans.Event(time, state)


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
            'active INTEGER NOT NULL)')
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS desk('
            'date INTEGER NOT NULL,'
            'state INTEGER NOT NULL)')

    def close(self):
        self.db.close()

    def insert_desk_event(self, event):
        self.db.execute('INSERT INTO desk values(?, ?)',
                        (event.index.timestamp(), event.data.integer()))
        self.db.commit()

    def insert_session_event(self, event):
        self.db.execute('INSERT INTO session values(?, ?)',
                        (event.index.timestamp(), event.data.integer()))
        self.db.commit()

    def get_desk_events(self):
        return get(self.db, 'SELECT * FROM desk ORDER BY date ASC')

    def get_session_events(self):
        return get(self.db, 'SELECT * FROM session ORDER BY date ASC')

    def get_desk_spans(self, initial, final):
        return spans.collect(
            default_data=Down(),
            initial=initial,
            final=final,
            events=self.get_desk_events())

    def get_session_spans(self, initial, final):
        return spans.collect(
            default_data=Inactive(),
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
            Active(),
            timedelta(0))

    def get_next_state(self):
        active_time = self.get_active_time()
        state = self.desk_latest.data
        return (state.limit() - active_time, state.next())

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
