from autodesk.spans import Event
from autodesk.states import INACTIVE, ACTIVE, DOWN, UP
from contextlib import closing
import logging
import sqlite3


def session_from_int(value):
    if value == 0:
        return INACTIVE
    elif value == 1:
        return ACTIVE
    else:
        raise ValueError('incorrect session state')


def desk_from_int(value):
    if value == 0:
        return DOWN
    elif value == 1:
        return UP
    else:
        raise ValueError('incorrect desk state')


def event_from_row(cursor, values):
    time = values[0]
    assert cursor.description[0][0] == 'date'
    col_name = cursor.description[1][0]
    if col_name == 'active':
        return Event(time, session_from_int(values[1]))
    elif col_name == 'state':
        return Event(time, desk_from_int(values[1]))
    else:
        raise ValueError('incorrect column names')


class SqliteDataStore:
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

    def set_desk(self, date, state):
        self.logger.debug(
            'set desk %s %s',
            date,
            state.test('down', 'up'))
        self.db.execute('INSERT INTO desk values(?, ?)',
                        (date, state.test(0, 1)))
        self.db.commit()

    def set_session(self, date, state):
        self.logger.debug(
            'set session %s %s',
            date,
            state.test('inactive', 'active'))
        self.db.execute('INSERT INTO session values(?, ?)',
                        (date, state.test(0, 1)))
        self.db.commit()
