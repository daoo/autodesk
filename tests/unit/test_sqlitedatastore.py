from autodesk.states import UP, DOWN, ACTIVE, INACTIVE
import autodesk.sqlitedatastore as sqlitedatastore
import pytest


def test_session_from_int():
    assert sqlitedatastore.session_from_int(0) == INACTIVE
    assert sqlitedatastore.session_from_int(1) == ACTIVE
    with pytest.raises(ValueError):
        sqlitedatastore.session_from_int(2)


def test_desk_from_int():
    assert sqlitedatastore.desk_from_int(0) == DOWN
    assert sqlitedatastore.desk_from_int(1) == UP
    with pytest.raises(ValueError):
        sqlitedatastore.desk_from_int(2)


def test_event_from_row_incorrect(mocker):
    cursor = mocker.MagicMock()
    cursor.description = [['date'], ['foobar']]
    values = [0, 0]
    with pytest.raises(ValueError):
        sqlitedatastore.event_from_row(cursor, values)
