from autodesk.states import UP, DOWN, INACTIVE, ACTIVE


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
