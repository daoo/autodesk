from autodesk.hardware.logging import LoggingPinFactory

import logging


def create_pin_factory(kind):
    logger = logging.getLogger("hardware")

    if kind == "raspberrypi":
        logger.info("using rpi hardware")
        return LoggingPinFactory(create_raspberry_pi())
    if kind == "ft232h":
        logger.info("using ft232h hardware")
        return LoggingPinFactory(create_ft232h())

    logger.info("using noop hardware")
    return LoggingPinFactory(create_noop())


def create_raspberry_pi():
    from autodesk.hardware.raspberrypi import RaspberryPiPinFactory

    return RaspberryPiPinFactory()


def create_ft232h():
    from autodesk.hardware.ft232h import Ft232hPinFactory

    return Ft232hPinFactory()


def create_noop():
    from autodesk.hardware.noop import NoopPinFactory

    return NoopPinFactory()
