from autodesk.hardware.logging import LoggingWrapper
import logging

def create_hardware(config):
    logger = logging.getLogger('hardware')

    desk = config['desk']
    delay = desk['delay']
    motor_pins = (
        desk['motor_pins']['down'],
        desk['motor_pins']['up'],
    )
    light_pin = desk['light_pin']
    if desk['hardware'] == 'raspberrypi':
        logger.info('using rpi hardware')
        return LoggingWrapper(
            create_raspberry_pi(delay, motor_pins, light_pin))
    elif desk['hardware'] == 'ft232h':
        logger.info('using ft232h hardware')
        return LoggingWrapper(
            create_ft232h(delay, motor_pins, light_pin))
    else:
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
