import RPi.GPIO as GPIO
import time


class RaspberryPi:
    def __init__(self, delay, motor_pins, light_pin):
        self.delay = delay
        self.motor_pins = motor_pins
        self.light_pin = light_pin

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.motor_pins[0], GPIO.OUT)
        GPIO.setup(self.motor_pins[1], GPIO.OUT)
        GPIO.setup(self.light_pin, GPIO.OUT)

    def close(self):
        GPIO.cleanup()

    def desk(self, state):
        pin = state.test(*self.motor_pins)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(self.delay)
        GPIO.output(pin, GPIO.LOW)

    def light(self, state):
        GPIO.output(self.light_pin, state.test(GPIO.LOW, GPIO.HIGH))