from collections.abc import Callable
from typing import cast

from autodesk.hardware.logging import LoggingPinFactory

import logging

from autodesk.hardware.types import HardwareKind, PinFactory


def create_pin_factory(kind: str) -> PinFactory:
    logger = logging.getLogger("hardware")
    builders: dict[HardwareKind, tuple[str, Callable[[], PinFactory]]] = {
        "raspberrypi": ("using rpi hardware", create_raspberry_pi),
        "ft232h": ("using ft232h hardware", create_ft232h),
        "noop": ("using noop hardware", create_noop),
    }

    if kind not in builders:
        raise ValueError(f"Unknown hardware kind: {kind!r}")

    kind_key = cast(HardwareKind, kind)
    message, builder = builders[kind_key]
    logger.info(message)
    return LoggingPinFactory(builder())


def create_raspberry_pi() -> PinFactory:
    from autodesk.hardware.raspberrypi import RaspberryPiPinFactory

    return RaspberryPiPinFactory()


def create_ft232h() -> PinFactory:
    from autodesk.hardware.ft232h import Ft232hPinFactory

    return Ft232hPinFactory()


def create_noop() -> PinFactory:
    from autodesk.hardware.noop import NoopPinFactory

    return NoopPinFactory()
