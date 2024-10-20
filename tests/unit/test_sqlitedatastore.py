import sqlite3

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

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
        "state SESSION NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS desk("
        "date TIMESTAMP NOT NULL,"
        "state DESK NOT NULL)"
    )
    connection.execute(
            "INSERT INTO session values(?, ?)",
            ("2023-01-09 20:07:00", 'inactive'))
    connection.execute(
            "INSERT INTO session values(?, ?)",
            ("2023-01-09 20:08:00", 'active'))
    connection.execute(
            "INSERT INTO desk values(?, ?)",
            ("2023-01-09 20:09:00", 'up'))
    connection.execute(
            "INSERT INTO desk values(?, ?)",
            ("2023-01-09 20:11:00", 'down'))
    connection.execute(
            "INSERT INTO session values(?, ?)",
            ("2023-01-09 20:12:00", 'inactive'))
    return connection


def test_constructor(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)
    assert data_store


def test_get_desk_events(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    expected_events = pd.DataFrame({
        "timestamp": [
            pd.Timestamp(2023, 1, 9, 20, 9, 0),
            pd.Timestamp(2023, 1, 9, 20, 11, 0)
            ],
        "state": [UP, DOWN]
    })
    assert_frame_equal(data_store.get_desk_events(), expected_events)


def test_get_session_events(logger_stub, db_with_old_tables):
    data_store = SqliteDataStore(logger_stub, db_with_old_tables)

    expected_events = pd.DataFrame({
        "timestamp": [
            pd.Timestamp(2023, 1, 9, 20, 7, 0),
            pd.Timestamp(2023, 1, 9, 20, 8, 0),
            pd.Timestamp(2023, 1, 9, 20, 12, 0)
            ],
        "state": [INACTIVE, ACTIVE, INACTIVE]
    })
    assert_frame_equal(data_store.get_session_events(), expected_events)

