import pytest

from autodesk.states import (
    Desk,
    Session,
    deserialize_desk_int,
    deserialize_session_int,
)


def test_down_next():
    assert Desk.DOWN.next() == Desk.UP


def test_up_next():
    assert Desk.UP.next() == Desk.DOWN


def test_down_is_down():
    assert Desk.DOWN.is_down
    assert not Desk.DOWN.is_up


def test_up_is_up():
    assert Desk.UP.is_up
    assert not Desk.UP.is_down


def test_inactive_next():
    assert Session.INACTIVE.next() == Session.ACTIVE


def test_active_next():
    assert Session.ACTIVE.next() == Session.INACTIVE


def test_inactive_is_inactive():
    assert Session.INACTIVE.is_inactive
    assert not Session.INACTIVE.is_active


def test_active_is_active():
    assert Session.ACTIVE.is_active
    assert not Session.ACTIVE.is_inactive


def test_labels():
    assert Desk.DOWN.label() == "down"
    assert Desk.UP.label() == "up"
    assert Session.INACTIVE.label() == "inactive"
    assert Session.ACTIVE.label() == "active"


def test_deserialize_desk_int():
    assert deserialize_desk_int(b"0") == Desk.DOWN
    assert deserialize_desk_int(b"1") == Desk.UP
    with pytest.raises(ValueError, match="Incorrect desk state \"b'2'\""):
        assert deserialize_desk_int(b"2")


def test_deserialize_session_int():
    assert deserialize_session_int(b"0") == Session.INACTIVE
    assert deserialize_session_int(b"1") == Session.ACTIVE
    with pytest.raises(ValueError, match="Incorrect session state \"b'2'\""):
        assert deserialize_session_int(b"2")
