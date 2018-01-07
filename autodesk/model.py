from contextlib import closing
from datetime import datetime, timedelta
import autodesk.spans as spans
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
    time = datetime.fromtimestamp(values[0])
    assert cursor.description[0][0] == 'date'
    col_name = cursor.description[1][0]
    state = None
    if col_name == 'active':
        state = session_from_int(values[1])
    elif col_name == 'state':
        state = desk_from_int(values[1])
    else:
        raise ValueError('incorrect column names')

    return spans.Event(time, state)


class Model:
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
                        (event.index.timestamp(), event.data.test(0, 1)))
        self.db.commit()

    def insert_session_event(self, event):
        self.db.execute('INSERT INTO session values(?, ?)',
                        (event.index.timestamp(), event.data.test(0, 1)))
        self.db.commit()

    def get(self, query):
        with closing(self.db.execute(query)) as cursor:
            return cursor.fetchall()

    def get_desk_events(self):
        return self.get('SELECT * FROM desk ORDER BY date ASC')

    def get_session_events(self):
        return self.get('SELECT * FROM session ORDER BY date ASC')

    def get_desk_spans(self, initial, final):
        return list(spans.collect(
            default_data=Down(),
            initial=initial,
            final=final,
            events=self.get_desk_events()))

    def get_session_spans(self, initial, final):
        return list(spans.collect(
            default_data=Inactive(),
            initial=initial,
            final=final,
            events=self.get_session_events()))
