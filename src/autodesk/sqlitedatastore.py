import datetime
import logging
import sqlite3

import autodesk.states as states


def adapt_datetime_epoch(val: datetime.datetime):
    return int(val.timestamp())


def convert_datetime(val):
    return datetime.datetime.fromisoformat(val.decode())


def convert_timestamp(val):
    return datetime.datetime.fromtimestamp(int(val))


sqlite3.register_adapter(datetime.datetime, adapt_datetime_epoch)
sqlite3.register_converter("timestamp", convert_datetime)
sqlite3.register_converter("unix_timestamp", convert_timestamp)

sqlite3.register_adapter(states.Desk, lambda desk: desk.value())
sqlite3.register_adapter(states.Session, lambda session: session.value())
sqlite3.register_converter("desk", states.deserialize_desk)
sqlite3.register_converter("session", states.deserialize_session)
sqlite3.register_converter("desk_int", states.deserialize_desk_int)
sqlite3.register_converter("session_int", states.deserialize_session_int)


def _migrate(
    logger: logging.Logger,
    connection: sqlite3.Connection,
    old_table: str,
    new_table: str,
    order_by: str,
):
    tables = connection.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{old_table}'",
    )
    name = tables.fetchone()
    if name:
        rows = connection.execute(f"SELECT * FROM {old_table} ORDER BY {order_by} ASC")
        data = rows.fetchall()
        logger.info(
            "migrating table %s with %d row(s) to %s",
            old_table,
            len(data),
            new_table,
        )
        connection.executemany(f"INSERT INTO {new_table} VALUES(?, ?)", data)
        connection.execute(f"DROP TABLE {old_table}")
        connection.commit()
        connection.execute("VACUUM")


class SqliteDataStore:
    def __init__(self, logger: logging.Logger, connection: sqlite3.Connection):
        self.logger = logger
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS session3("
            "timestamp UNIX_TIMESTAMP NOT NULL,"
            "state SESSION_INT NOT NULL)",
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS desk3("
            "timestamp UNIX_TIMESTAMP NOT NULL,"
            "state DESK_INT NOT NULL)",
        )

        _migrate(self.logger, self.connection, "desk", "desk3", "date")
        _migrate(self.logger, self.connection, "session", "session3", "date")
        _migrate(self.logger, self.connection, "desk2", "desk3", "timestamp")
        _migrate(self.logger, self.connection, "session2", "session3", "timestamp")

    @staticmethod
    def open(path: str):
        logger = logging.getLogger("sqlite3")
        logger.info("Opening database %s", path)
        connection = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        return SqliteDataStore(logger, connection)

    def close(self) -> None:
        self.connection.close()

    def get_last_desk_event(self) -> tuple[datetime.datetime, states.Desk] | None:
        row = self.connection.execute(
            "SELECT timestamp, state FROM desk3 ORDER BY timestamp DESC LIMIT 1",
        ).fetchone()
        return (row[0], row[1]) if row else None

    def get_last_session_event(
        self,
    ) -> tuple[datetime.datetime, states.Session] | None:
        row = self.connection.execute(
            "SELECT timestamp, state FROM session3 ORDER BY timestamp DESC LIMIT 1",
        ).fetchone()
        return (row[0], row[1]) if row else None

    def get_last_desk_event_before(
        self,
        at: datetime.datetime,
    ) -> tuple[datetime.datetime, states.Desk] | None:
        row = self.connection.execute(
            "SELECT timestamp, state FROM desk3 "
            "WHERE timestamp <= ? "
            "ORDER BY timestamp DESC LIMIT 1",
            (at,),
        ).fetchone()
        return (row[0], row[1]) if row else None

    def get_last_session_event_before(
        self,
        at: datetime.datetime,
    ) -> tuple[datetime.datetime, states.Session] | None:
        row = self.connection.execute(
            "SELECT timestamp, state FROM session3 "
            "WHERE timestamp <= ? "
            "ORDER BY timestamp DESC LIMIT 1",
            (at,),
        ).fetchone()
        return (row[0], row[1]) if row else None

    def get_desk_events_between(
        self,
        initial: datetime.datetime,
        final: datetime.datetime,
    ) -> list[tuple[datetime.datetime, states.Desk]]:
        rows = self.connection.execute(
            "SELECT timestamp, state FROM desk3 "
            "WHERE timestamp >= ? AND timestamp <= ? "
            "ORDER BY timestamp ASC",
            (initial, final),
        ).fetchall()
        return [(at, state) for at, state in rows]

    def get_session_events_between(
        self,
        initial: datetime.datetime,
        final: datetime.datetime,
    ) -> list[tuple[datetime.datetime, states.Session]]:
        rows = self.connection.execute(
            "SELECT timestamp, state FROM session3 "
            "WHERE timestamp >= ? AND timestamp <= ? "
            "ORDER BY timestamp ASC",
            (initial, final),
        ).fetchall()
        return [(at, state) for at, state in rows]

    def set_desk(self, at: datetime.datetime, state: states.Desk) -> None:
        self.logger.debug("set desk %s %s", at, state.test("down", "up"))
        values = (at, state)
        self.connection.execute("INSERT INTO desk3 values(?, ?)", values)
        self.connection.commit()

    def set_session(self, at: datetime.datetime, state: states.Session) -> None:
        self.logger.debug("set session %s %s", at, state.test("inactive", "active"))
        values = (at, state)
        self.connection.execute("INSERT INTO session3 values(?, ?)", values)
        self.connection.commit()
