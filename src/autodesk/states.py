class Desk:
    def __init__(self, state: bool):
        self._state = state

    def value(self) -> int:
        return int(self._state)

    def next(self) -> "Desk":
        return Desk(not self._state)

    def test[T](self, a: T, b: T) -> T:
        return b if self._state else a

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Desk) and self._state == other._state


class Session:
    def __init__(self, state: bool):
        self._state = state

    def value(self) -> int:
        return int(self._state)

    def next(self) -> "Session":
        return Session(not self._state)

    def test[T](self, a: T, b: T) -> T:
        return b if self._state else a

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Session) and self._state == other._state


DOWN: Desk = Desk(False)
UP: Desk = Desk(True)

INACTIVE: Session = Session(False)
ACTIVE: Session = Session(True)


def deserialize_session(value: bytes | str) -> Session:
    if value in (b"inactive", "inactive"):
        return INACTIVE
    if value in (b"active", "active"):
        return ACTIVE

    raise ValueError(f'Incorrect session state "{value!r}"')


def deserialize_desk(value: bytes | str) -> Desk:
    if value in (b"down", "down"):
        return DOWN
    if value in (b"up", "up"):
        return UP

    raise ValueError(f'Incorrect desk state "{value!r}".')


def deserialize_session_int(value: bytes) -> Session:
    if value == b"0":
        return INACTIVE
    if value == b"1":
        return ACTIVE

    raise ValueError(f'Incorrect session state "{value!r}".')


def deserialize_desk_int(value: bytes) -> Desk:
    if value == b"0":
        return DOWN
    if value == b"1":
        return UP

    raise ValueError(f'Incorrect desk state "{value!r}".')
