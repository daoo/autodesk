import pytest

from autodesk.states import (
    ACTIVE,
    DOWN,
    INACTIVE,
    UP,
    deserialize_desk_int,
    deserialize_session_int,
)


def test_down_next():
    assert DOWN.next() == UP


def test_up_next():
    assert UP.next() == DOWN


def test_down_test():
    assert DOWN.test(0, 1) == 0


def test_up_test():
    assert UP.test(0, 1) == 1


def test_inactive_next():
    assert INACTIVE.next() == ACTIVE


def test_active_next():
    assert ACTIVE.next() == INACTIVE


def test_inactive_test():
    assert INACTIVE.test(0, 1) == 0


def test_active_test():
    assert ACTIVE.test(0, 1) == 1


def test_deserialize_desk_int():
    assert deserialize_desk_int(b"0") == DOWN
    assert deserialize_desk_int(b"1") == UP
    with pytest.raises(ValueError):
        assert deserialize_desk_int(b"2")


def test_deserialize_session_int():
    assert deserialize_session_int(b"0") == INACTIVE
    assert deserialize_session_int(b"1") == ACTIVE
    with pytest.raises(ValueError):
        assert deserialize_session_int(b"2")
