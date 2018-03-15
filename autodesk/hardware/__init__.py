from autodesk.hardware.logging import LoggingWrapper
import logging

class HardwareFactory:
    def __init__(self):
        self.logger = logging.getLogger('hardware_factory')

    def create(self, config):
        desk = config['desk']
        delay = desk['delay']
        motor_pins = (
            desk['motor_pins']['down'],
            desk['motor_pins']['up'],
        )
        light_pin = desk['light_pin']
        if desk['hardware'] == 'raspberrypi':
            return LoggingWrapper(
                self.create_raspberry_pi(delay, motor_pins, light_pin))
        elif desk['hardware'] == 'ft232h':
            return LoggingWrapper(
                self.create_ft232h(delay, motor_pins, light_pin))
        else:
            return LoggingWrapper(self.create_noop())

    def create_raspberry_pi(self, delay, motor_pins, light_pin):
        self.logger.info('using rpi hardware')
        from autodesk.hardware.raspberrypi import RaspberryPi
        return RaspberryPi(delay, motor_pins, light_pin)

    def create_ft232h(self, delay, motor_pins, light_pin):
        self.logger.info('using ft232h hardware')
        from autodesk.hardware.ft232h import Ft232h
        return Ft232h(delay, motor_pins, light_pin)

    def create_noop(self):
        self.logger.info('using noop hardware')
        from autodesk.hardware.noop import Noop
        return Noop()
