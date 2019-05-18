import autodesk.states as states
import logging
import pandas as pd
import sqlite3


sqlite3.register_adapter(states.Down, lambda _: 'down')
sqlite3.register_adapter(states.Up, lambda _: 'up')
sqlite3.register_adapter(states.Inactive, lambda _: 'inactive')
sqlite3.register_adapter(states.Active, lambda _: 'active')
sqlite3.register_converter('desk', states.deserialize_desk)
sqlite3.register_converter('session', states.deserialize_session)


class SqliteDataStore:
    def __init__(self, path):
        self.logger = logging.getLogger('sqlite3')
        self.logger.info('Opening database %s', path)
        self.connection = sqlite3.connect(
            path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.execute(
            'CREATE TABLE IF NOT EXISTS session('
            'date TIMESTAMP NOT NULL,'
            'state SESSION NOT NULL)')
        self.connection.execute(
            'CREATE TABLE IF NOT EXISTS desk('
            'date TIMESTAMP NOT NULL,'
            'state DESK NOT NULL)')

    def close(self):
        self.connection.close()

    def _get(self, query):
        return pd.read_sql_query(query, self.connection)

    def get_desk_events(self):
        return self._get('SELECT * FROM desk ORDER BY date ASC')

    def get_session_events(self):
        return self._get('SELECT * FROM session ORDER BY date ASC')

    def set_desk(self, date, state):
        self.logger.debug(
            'set desk %s %s',
            date,
            state.test('down', 'up'))
        values = (date.to_pydatetime(), state)
        self.connection.execute('INSERT INTO desk values(?, ?)', values)
        self.connection.commit()

    def set_session(self, date, state):
        self.logger.debug(
            'set session %s %s',
            date,
            state.test('inactive', 'active'))
        values = (date.to_pydatetime(), state)
        self.connection.execute('INSERT INTO session values(?, ?)', values)
        self.connection.commit()
