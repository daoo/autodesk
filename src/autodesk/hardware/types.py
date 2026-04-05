from typing import Literal, Protocol, cast

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


def validate_pin_value(value: int) -> PinValue:
    if value not in (0, 1):
        raise ValueError(f"Pin value must be 0 or 1 but got {value}")
    return cast(PinValue, value)
