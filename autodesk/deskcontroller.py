import time


class DeskController:
    def __init__(self, delay, pin_down, pin_up):
        self.delay = delay
        self.pin_down = pin_down
        self.pin_up = pin_up

    def move(self, state):
        pin = state.test(self.pin_down, self.pin_up)
        pin.write(1)
        time.sleep(self.delay)
        pin.write(0)
