import time


class DeskController:
    def __init__(self, delay: float, pin_down, pin_up, pin_light):
        self.delay = delay
        self.pin_down = pin_down
        self.pin_up = pin_up
        self.pin_light = pin_light

    def move(self, state):
        pin = state.test(self.pin_down, self.pin_up)
        self.pin_light.write(1)
        pin.write(1)
        time.sleep(self.delay)
        pin.write(0)
        self.pin_light.write(0)
