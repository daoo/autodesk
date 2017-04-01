import RPi.GPIO as GPIO
import time


DELAY = 15


class Hardware:
    def __init__(self, pins):
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
        time.sleep(DELAY)
        GPIO.output(pin, GPIO.LOW)
