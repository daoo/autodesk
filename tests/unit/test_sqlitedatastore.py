import sqlite3
from datetime import datetime

import pytest

from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.states import Desk, Session


@pytest.fixture
def logger_stub(mocker):
    return mocker.MagicMock()


@pytest.fixture
def db_with_events():
    connection = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS session3("
        "timestamp UNIX_TIMESTAMP NOT NULL,"
        "state SESSION_INT NOT NULL)",
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS desk3("
        "timestamp UNIX_TIMESTAMP NOT NULL,"
        "state DESK_INT NOT NULL)",
    )
    connection.execute(
        "INSERT INTO session3 values(?, ?)",
        (datetime(2023, 1, 9, 20, 7, 0), Session.INACTIVE),
    )
    connection.execute(
        "INSERT INTO session3 values(?, ?)",
        (datetime(2023, 1, 9, 20, 8, 0), Session.ACTIVE),
    )
    connection.execute(
        "INSERT INTO desk3 values(?, ?)",
        (datetime(2023, 1, 9, 20, 9, 0), Desk.UP),
    )
    connection.execute(
        "INSERT INTO desk3 values(?, ?)",
        (datetime(2023, 1, 9, 20, 11, 0), Desk.DOWN),
    )
    connection.execute(
        "INSERT INTO session3 values(?, ?)",
        (datetime(2023, 1, 9, 20, 12, 0), Session.INACTIVE),
    )
    yield connection
    connection.close()


def test_constructor(logger_stub, db_with_events):
    data_store = SqliteDataStore(logger_stub, db_with_events)
    assert data_store


def test_get_desk_events_between_full_range(logger_stub, db_with_events):
    data_store = SqliteDataStore(logger_stub, db_with_events)

    expected_events = [
        (datetime(2023, 1, 9, 20, 9, 0), Desk.UP),
        (datetime(2023, 1, 9, 20, 11, 0), Desk.DOWN),
    ]
    assert (
        data_store.get_desk_events_between(
            datetime(2023, 1, 9, 20, 0, 0),
            datetime(2023, 1, 9, 21, 0, 0),
        )
        == expected_events
    )


def test_get_session_events_between_full_range(logger_stub, db_with_events):
    data_store = SqliteDataStore(logger_stub, db_with_events)

    expected_events = [
        (datetime(2023, 1, 9, 20, 7, 0), Session.INACTIVE),
        (datetime(2023, 1, 9, 20, 8, 0), Session.ACTIVE),
        (datetime(2023, 1, 9, 20, 12, 0), Session.INACTIVE),
    ]
    assert (
        data_store.get_session_events_between(
            datetime(2023, 1, 9, 20, 0, 0),
            datetime(2023, 1, 9, 21, 0, 0),
        )
        == expected_events
    )


def test_get_last_desk_event(logger_stub, db_with_events):
    data_store = SqliteDataStore(logger_stub, db_with_events)

    assert data_store.get_last_desk_event() == (
        datetime(2023, 1, 9, 20, 11, 0),
        Desk.DOWN,
    )


def test_get_last_session_event(logger_stub, db_with_events):
    data_store = SqliteDataStore(logger_stub, db_with_events)

    assert data_store.get_last_session_event() == (
        datetime(2023, 1, 9, 20, 12, 0),
        Session.INACTIVE,
    )


def test_get_last_desk_event_before(logger_stub, db_with_events):
    data_store = SqliteDataStore(logger_stub, db_with_events)

    assert data_store.get_last_desk_event_before(
        datetime(2023, 1, 9, 20, 10, 0),
    ) == (datetime(2023, 1, 9, 20, 9, 0), Desk.UP)


def test_get_last_session_event_before(logger_stub, db_with_events):
    data_store = SqliteDataStore(logger_stub, db_with_events)

    assert data_store.get_last_session_event_before(
        datetime(2023, 1, 9, 20, 8, 0),
    ) == (datetime(2023, 1, 9, 20, 8, 0), Session.ACTIVE)


def test_get_desk_events_between(logger_stub, db_with_events):
    data_store = SqliteDataStore(logger_stub, db_with_events)

    assert data_store.get_desk_events_between(
        datetime(2023, 1, 9, 20, 10, 0),
        datetime(2023, 1, 9, 20, 12, 0),
    ) == [(datetime(2023, 1, 9, 20, 11, 0), Desk.DOWN)]


def test_get_session_events_between(logger_stub, db_with_events):
    data_store = SqliteDataStore(logger_stub, db_with_events)

    assert data_store.get_session_events_between(
        datetime(2023, 1, 9, 20, 8, 0),
        datetime(2023, 1, 9, 20, 12, 0),
    ) == [
        (datetime(2023, 1, 9, 20, 8, 0), Session.ACTIVE),
        (datetime(2023, 1, 9, 20, 12, 0), Session.INACTIVE),
    ]
