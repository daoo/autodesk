class Desk:
    def __init__(self, state: bool):
        self._state = state

    def value(self):
        return int(self._state)

    def next(self):
        return Desk(not self._state)

    def test[T](self, a: T, b: T) -> T:
        return b if self._state else a

    def __eq__(self, other):
        return isinstance(other, Desk) and self._state == other._state


class Session:
    def __init__(self, state: bool):
        self._state = state

    def value(self):
        return int(self._state)

    def next(self):
        return Session(not self._state)

    def test[T](self, a: T, b: T) -> T:
        return b if self._state else a

    def __eq__(self, other):
        return isinstance(other, Session) and self._state == other._state


DOWN = Desk(False)
UP = Desk(True)

INACTIVE = Session(False)
ACTIVE = Session(True)


def deserialize_session(value: bytes | str):
    if value in (b"inactive", "inactive"):
        return INACTIVE
    if value in (b"active", "active"):
        return ACTIVE

    raise ValueError(f'Incorrect session state "{value!r}"')


def deserialize_desk(value: bytes | str):
    if value in (b"down", "down"):
        return DOWN
    if value in (b"up", "up"):
        return UP

    raise ValueError(f'Incorrect desk state "{value!r}".')


def deserialize_session_int(value: bytes):
    if value == b"0":
        return INACTIVE
    if value == b"1":
        return ACTIVE

    raise ValueError(f'Incorrect session state "{value!r}".')


def deserialize_desk_int(value: bytes):
    if value == b"0":
        return DOWN
    if value == b"1":
        return UP

    raise ValueError(f'Incorrect desk state "{value!r}".')
