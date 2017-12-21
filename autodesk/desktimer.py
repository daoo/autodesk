import threading

class DeskTimer:
    def __init__(self, action):
        self.action = action
        self.timer = None

    def schedule(self, next_state):
        (delay, target) = next_state
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(
            delay.total_seconds(),
            self.action,
            (target,))
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.cancel()

    def __repr__(self):
        return 'DeskTimer(server={}, timer={})'.format(
            self.server,
            self.timer)
