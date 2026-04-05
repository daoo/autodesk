import datetime
import logging
import sqlite3
from typing import Any, cast

import autodesk.states as states

type DeskEvent = tuple[datetime.datetime, states.Desk]
type SessionEvent = tuple[datetime.datetime, states.Session]

def adapt_datetime_epoch(val: datetime.datetime) -> int:
    utc = val.replace(tzinfo=datetime.UTC)
    return int(utc.timestamp())


def convert_timestamp(val: bytes) -> datetime.datetime:
    utc = datetime.datetime.fromtimestamp(int(val), tz=datetime.UTC)
    return utc.replace(tzinfo=None)


sqlite3.register_adapter(datetime.datetime, adapt_datetime_epoch)
sqlite3.register_converter("unix_timestamp", convert_timestamp)

sqlite3.register_adapter(states.Desk, lambda desk: desk.value)
sqlite3.register_adapter(states.Session, lambda session: session.value)
sqlite3.register_converter("desk_int", states.deserialize_desk_int)
sqlite3.register_converter("session_int", states.deserialize_session_int)


class SqliteDataStore:
    def __init__(self, logger: logging.Logger, connection: sqlite3.Connection) -> None:
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

    @staticmethod
    def open(path: str) -> "SqliteDataStore":
        logger = logging.getLogger("sqlite3")
        logger.info("Opening database %s", path)
        connection = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        return SqliteDataStore(logger, connection)

    def close(self) -> None:
        self.connection.close()

    def _get_last_event(self, table: str) -> tuple[datetime.datetime, Any] | None:
        row = self.connection.execute(
            f"SELECT timestamp, state FROM {table} ORDER BY timestamp DESC LIMIT 1",
        ).fetchone()
        return (row[0], row[1]) if row else None

    def _get_last_event_before(
        self,
        table: str,
        at: datetime.datetime,
    ) -> tuple[datetime.datetime, Any] | None:
        row = self.connection.execute(
            f"SELECT timestamp, state FROM {table} "
            "WHERE timestamp <= ? "
            "ORDER BY timestamp DESC LIMIT 1",
            (at,),
        ).fetchone()
        return (row[0], row[1]) if row else None

    def _get_events_between(
        self,
        table: str,
        initial: datetime.datetime,
        final: datetime.datetime,
    ) -> list[tuple[datetime.datetime, Any]]:
        rows = self.connection.execute(
            f"SELECT timestamp, state FROM {table} "
            "WHERE timestamp >= ? AND timestamp <= ? "
            "ORDER BY timestamp ASC",
            (initial, final),
        ).fetchall()
        return [(at, state) for at, state in rows]

    def get_last_desk_event(self) -> DeskEvent | None:
        row = self._get_last_event("desk3")
        return cast(DeskEvent | None, row)

    def get_last_session_event(
        self,
    ) -> SessionEvent | None:
        row = self._get_last_event("session3")
        return cast(SessionEvent | None, row)

    def get_last_session_event_before(
        self,
        at: datetime.datetime,
    ) -> SessionEvent | None:
        row = self._get_last_event_before("session3", at)
        return cast(SessionEvent | None, row)

    def get_last_desk_event_before(
        self,
        at: datetime.datetime,
    ) -> DeskEvent | None:
        row = self._get_last_event_before("desk3", at)
        return cast(DeskEvent | None, row)

    def get_desk_events_between(
        self,
        initial: datetime.datetime,
        final: datetime.datetime,
    ) -> list[DeskEvent]:
        rows = self._get_events_between("desk3", initial, final)
        return cast(list[DeskEvent], rows)

    def get_session_events_between(
        self,
        initial: datetime.datetime,
        final: datetime.datetime,
    ) -> list[SessionEvent]:
        rows = self._get_events_between("session3", initial, final)
        return cast(list[SessionEvent], rows)

    def set_desk(self, at: datetime.datetime, state: states.Desk) -> None:
        self.logger.debug("set desk %s %s", at, state.label())
        values = (at, state)
        self.connection.execute("INSERT INTO desk3 values(?, ?)", values)
        self.connection.commit()

    def set_session(self, at: datetime.datetime, state: states.Session) -> None:
        self.logger.debug("set session %s %s", at, state.label())
        values = (at, state)
        self.connection.execute("INSERT INTO session3 values(?, ?)", values)
        self.connection.commit()
