from enum import IntEnum


class Desk(IntEnum):
    DOWN = 0
    UP = 1

    @property
    def is_down(self) -> bool:
        return self is Desk.DOWN

    @property
    def is_up(self) -> bool:
        return self is Desk.UP

    def next(self) -> "Desk":
        return Desk.UP if self.is_down else Desk.DOWN

    def label(self) -> str:
        return "up" if self.is_up else "down"


class Session(IntEnum):
    INACTIVE = 0
    ACTIVE = 1

    @property
    def is_inactive(self) -> bool:
        return self is Session.INACTIVE

    @property
    def is_active(self) -> bool:
        return self is Session.ACTIVE

    def next(self) -> "Session":
        return Session.ACTIVE if self.is_inactive else Session.INACTIVE

    def label(self) -> str:
        return "active" if self.is_active else "inactive"


def deserialize_session(value: bytes | str) -> Session:
    if value in (b"inactive", "inactive"):
        return Session.INACTIVE
    if value in (b"active", "active"):
        return Session.ACTIVE

    raise ValueError(f'Incorrect session state "{value!r}"')


def deserialize_desk(value: bytes | str) -> Desk:
    if value in (b"down", "down"):
        return Desk.DOWN
    if value in (b"up", "up"):
        return Desk.UP

    raise ValueError(f'Incorrect desk state "{value!r}".')


def deserialize_session_int(value: bytes) -> Session:
    if value == b"0":
        return Session.INACTIVE
    if value == b"1":
        return Session.ACTIVE

    raise ValueError(f'Incorrect session state "{value!r}".')


def deserialize_desk_int(value: bytes) -> Desk:
    if value == b"0":
        return Desk.DOWN
    if value == b"1":
        return Desk.UP

    raise ValueError(f'Incorrect desk state "{value!r}".')
