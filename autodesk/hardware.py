import RPi.GPIO as GPIO
import time


class Hardware:
    def __init__(self, delay, pins):
        self.delay = delay
        self.pins = pins

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)

    def cleanup(self):
        GPIO.cleanup()

    def go(self, state):
        pin = state.test(*self.pins)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(self.delay)
        GPIO.output(pin, GPIO.LOW)
