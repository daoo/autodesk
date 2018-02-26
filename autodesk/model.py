from contextlib import closing
from datetime import datetime, time
import autodesk.spans as spans
import logging
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
    state = None
    if col_name == 'active':
        state = session_from_int(values[1])
    elif col_name == 'state':
        state = desk_from_int(values[1])
    else:
        raise ValueError('incorrect column names')

    return spans.Event(time, state)


class Operation:
    def __init__(self):
        self.allowance_start = time(8, 0, 0)
        self.allowance_end = time(18, 0, 0)

    def allow(self, at):
        monday = 0
        friday = 4
        time_at = time(at.hour, at.minute, at.second)
        weekday = at.weekday()
        return \
            time_at >= self.allowance_start and \
            time_at <= self.allowance_end and \
            weekday >= monday and weekday <= friday


class Model:
    def __init__(self, path, operation):
        self.logger = logging.getLogger('model')
        self.observers = []
        self.operation = operation
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

    def add_observer(self, observer):
        self.observers.append(observer)

    def close(self):
        self.db.close()

    def set_desk(self, event):
        self.logger.debug(
            'set desk %s %s',
            event.index,
            event.data.test('down', 'up'))
        if not self.operation.allow(event.index):
            self.logger.warning('desk operation not allowed')
            for observer in self.observers:
                observer.desk_change_disallowed(event)
            return False

        self.db.execute('INSERT INTO desk values(?, ?)',
                        (event.index, event.data.test(0, 1)))
        self.db.commit()
        for observer in self.observers:
            observer.desk_changed(event)
        return True

    def set_session(self, event):
        self.logger.debug(
            'set session %s %s',
            event.index,
            event.data.test('inactive', 'active'))
        self.db.execute('INSERT INTO session values(?, ?)',
                        (event.index, event.data.test(0, 1)))
        self.db.commit()
        for observer in self.observers:
            observer.session_changed(event)

    def _get(self, query):
        with closing(self.db.execute(query)) as cursor:
            return cursor.fetchall()

    def get_desk_events(self):
        return self._get('SELECT * FROM desk ORDER BY date ASC')

    def get_session_events(self):
        return self._get('SELECT * FROM session ORDER BY date ASC')

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
