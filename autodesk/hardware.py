import autodesk.gpio as GPIO
import logging
import time


class Hardware:
    def __init__(self, delay, motor_pins, light_pin):
        self.logger = logging.getLogger('hardware')
        self.delay = delay
        self.motor_pins = motor_pins
        self.light_pin = light_pin

    def init(self):
        self.logger.info('init')
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.motor_pins[0], GPIO.OUT)
        GPIO.setup(self.motor_pins[1], GPIO.OUT)
        GPIO.setup(self.light_pin, GPIO.OUT)

    def close(self):
        self.logger.info('close')
        GPIO.cleanup()

    def go(self, state):
        self.logger.info('desk %s', state.test('down', 'up'))
        pin = state.test(*self.motor_pins)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(self.delay)
        GPIO.output(pin, GPIO.LOW)

    def light(self, state):
        self.logger.info('light %s', state.test('off', 'on'))
        GPIO.output(self.light_pin, state.test(GPIO.LOW, GPIO.HIGH))
