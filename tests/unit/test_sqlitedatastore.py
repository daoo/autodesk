import sqlite3
from datetime import datetime

import pytest

from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.states import ACTIVE, DOWN, INACTIVE, UP


@pytest.fixture
def logger_stub(mocker):
    return mocker.MagicMock()


@pytest.fixture
def db_with_old_tables():
    connection = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS session("
        "date TIMESTAMP NOT NULL,"
        "state SESSION NOT NULL)",
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS desk(date TIMESTAMP NOT NULL,state DESK NOT NULL)",
    )
    connection.execute(
        "INSERT INTO session values(?, ?)", ("2023-01-09 20:07:00", "inactive")
    )
    connection.execute(
        "INSERT INTO session values(?, ?)", ("2023-01-09 20:08:00", "active")
    )
    connection.execute("INSERT INTO desk values(?, ?)", ("2023-01-09 20:09:00", "up"))
    connection.execute("INSERT INTO desk values(?, ?)", ("2023-01-09 20:11:00", "down"))
    connection.execute(
        "INSERT INTO session values(?, ?)", ("2023-01-09 20:12:00", "inactive")
    )
    yield connection
    connection.close()


def test_constructor(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)
    assert data_store


def test_get_desk_events_between_full_range(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    expected_events = [
        (datetime(2023, 1, 9, 20, 9, 0), UP),
        (datetime(2023, 1, 9, 20, 11, 0), DOWN),
    ]
    assert data_store.get_desk_events_between(
        datetime(2023, 1, 9, 20, 0, 0),
        datetime(2023, 1, 9, 21, 0, 0),
    ) == expected_events


def test_get_session_events_between_full_range(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    expected_events = [
        (datetime(2023, 1, 9, 20, 7, 0), INACTIVE),
        (datetime(2023, 1, 9, 20, 8, 0), ACTIVE),
        (datetime(2023, 1, 9, 20, 12, 0), INACTIVE),
    ]
    assert data_store.get_session_events_between(
        datetime(2023, 1, 9, 20, 0, 0),
        datetime(2023, 1, 9, 21, 0, 0),
    ) == expected_events


def test_get_last_desk_event(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    assert data_store.get_last_desk_event() == (datetime(2023, 1, 9, 20, 11, 0), DOWN)


def test_get_last_session_event(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    assert data_store.get_last_session_event() == (
        datetime(2023, 1, 9, 20, 12, 0),
        INACTIVE,
    )


def test_get_last_desk_event_before(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    assert data_store.get_last_desk_event_before(
        datetime(2023, 1, 9, 20, 10, 0),
    ) == (datetime(2023, 1, 9, 20, 9, 0), UP)


def test_get_last_session_event_before(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    assert data_store.get_last_session_event_before(
        datetime(2023, 1, 9, 20, 8, 0),
    ) == (datetime(2023, 1, 9, 20, 8, 0), ACTIVE)


def test_get_desk_events_between(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    assert data_store.get_desk_events_between(
        datetime(2023, 1, 9, 20, 10, 0),
        datetime(2023, 1, 9, 20, 12, 0),
    ) == [(datetime(2023, 1, 9, 20, 11, 0), DOWN)]


def test_get_session_events_between(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    assert data_store.get_session_events_between(
        datetime(2023, 1, 9, 20, 8, 0),
        datetime(2023, 1, 9, 20, 12, 0),
    ) == [
        (datetime(2023, 1, 9, 20, 8, 0), ACTIVE),
        (datetime(2023, 1, 9, 20, 12, 0), INACTIVE),
    ]
