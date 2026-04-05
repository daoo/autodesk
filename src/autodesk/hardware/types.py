from typing import Literal, Protocol

type PinValue = Literal[0, 1]
type HardwareKind = Literal["raspberrypi", "ft232h", "noop"]


class InputPin(Protocol):
    pin: int

    def read(self) -> PinValue: ...


class OutputPin(Protocol):
    pin: int

    def write(self, value: PinValue) -> None: ...


class PinFactory(Protocol):
    def close(self) -> None: ...

    def create_input(self, pin: int) -> InputPin: ...

    def create_output(self, pin: int) -> OutputPin: ...
