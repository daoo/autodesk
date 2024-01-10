import autodesk.states as states
import datetime
import logging
import pandas as pd
import sqlite3


def adapt_datetime_epoch(val):
    return int(val.timestamp())


def convert_datetime(val):
    return datetime.datetime.fromisoformat(val.decode())


def convert_timestamp(val):
    return datetime.datetime.fromtimestamp(int(val))


sqlite3.register_adapter(datetime.datetime, adapt_datetime_epoch)
sqlite3.register_converter("timestamp", convert_datetime)
sqlite3.register_converter("unix_timestamp", convert_timestamp)

sqlite3.register_adapter(states.Down, lambda _: 0)
sqlite3.register_adapter(states.Up, lambda _: 1)
sqlite3.register_adapter(states.Inactive, lambda _: 0)
sqlite3.register_adapter(states.Active, lambda _: 1)
sqlite3.register_converter("desk", states.deserialize_desk)
sqlite3.register_converter("session", states.deserialize_session)
sqlite3.register_converter("desk_int", states.deserialize_desk_int)
sqlite3.register_converter("session_int", states.deserialize_session_int)


def _migrate(logger, connection, old_table, new_table, order_by):
    tables = connection.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{old_table}'"
    )
    name = tables.fetchone()
    if name:
        rows = connection.execute(f"SELECT * FROM {old_table} ORDER BY {order_by} ASC")
        data = rows.fetchall()
        logger.info(
            "migrating table %s with %d row(s) to %s", old_table, len(data), new_table
        )
        connection.executemany(f"INSERT INTO {new_table} VALUES(?, ?)", data)
        connection.execute(f"DROP TABLE {old_table}")
        connection.commit()
        connection.execute("VACUUM")


class SqliteDataStore:
    def __init__(self, logger, connection):
        self.logger = logger
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS session3("
            "timestamp UNIX_TIMESTAMP NOT NULL,"
            "state SESSION_INT NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS desk3("
            "timestamp UNIX_TIMESTAMP NOT NULL,"
            "state DESK_INT NOT NULL)"
        )

        _migrate(self.logger, self.connection, "desk", "desk3", "date")
        _migrate(self.logger, self.connection, "session", "session3", "date")
        _migrate(self.logger, self.connection, "desk2", "desk3", "timestamp")
        _migrate(self.logger, self.connection, "session2", "session3", "timestamp")

    @staticmethod
    def open(path):
        logger = logging.getLogger("sqlite3")
        logger.info("Opening database %s", path)
        connection = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        return SqliteDataStore(logger, connection)

    def close(self):
        self.connection.close()

    def _get(self, query):
        return pd.read_sql_query(query, self.connection)

    def get_desk_events(self):
        return self._get("SELECT * FROM desk3 ORDER BY timestamp ASC")

    def get_session_events(self):
        return self._get("SELECT * FROM session3 ORDER BY timestamp ASC")

    def set_desk(self, at, state):
        self.logger.debug("set desk %s %s", at, state.test("down", "up"))
        values = (at.to_pydatetime(), state)
        self.connection.execute("INSERT INTO desk3 values(?, ?)", values)
        self.connection.commit()

    def set_session(self, at, state):
        self.logger.debug("set session %s %s", at, state.test("inactive", "active"))
        values = (at.to_pydatetime(), state)
        self.connection.execute("INSERT INTO session3 values(?, ?)", values)
        self.connection.commit()
