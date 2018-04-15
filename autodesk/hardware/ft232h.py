import Adafruit_GPIO as GPIO
import FT232H
import time


class Ft232h:
    def __init__(self, delay, motor_pins, light_pin):
        self.delay = delay
        self.motor_pins = motor_pins
        self.light_pin = light_pin

        FT232H.use_FT232H()
        self.device = FT232H.FT232H()

        self.device.setup(self.motor_pins[0], GPIO.OUT)
        self.device.setup(self.motor_pins[1], GPIO.OUT)
        self.device.setup(self.light_pin, GPIO.OUT)

    def close(self):
        self.device.close()

    def desk(self, state):
        pin = state.test(*self.motor_pins)
        self.device.output(pin, GPIO.HIGH)
        time.sleep(self.delay)
        self.device.output(pin, GPIO.LOW)

    def light(self, state):
        gpio = state.test(GPIO.LOW, GPIO.HIGH)
        self.device.output(self.light_pin, gpio)
