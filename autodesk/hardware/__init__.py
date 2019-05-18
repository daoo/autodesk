from autodesk.hardware.logging import LoggingWrapper
import logging


def create_hardware(kind, delay, motor_pins, light_pin):
    logger = logging.getLogger('hardware')

    if kind == 'raspberrypi':
        logger.info('using rpi hardware')
        return LoggingWrapper(
            create_raspberry_pi(delay, motor_pins, light_pin))
    if kind == 'ft232h':
        logger.info('using ft232h hardware')
        return LoggingWrapper(
            create_ft232h(delay, motor_pins, light_pin))

    logger.info('using noop hardware')
    return LoggingWrapper(create_noop())


def create_raspberry_pi(delay, motor_pins, light_pin):
    from autodesk.hardware.raspberrypi import RaspberryPi
    return RaspberryPi(delay, motor_pins, light_pin)


def create_ft232h(delay, motor_pins, light_pin):
    from autodesk.hardware.ft232h import Ft232h
    return Ft232h(delay, motor_pins, light_pin)


def create_noop():
    from autodesk.hardware.noop import Noop
    return Noop()
