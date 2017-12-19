import threading


class Timer:
    def __init__(self, action):
        self.timer = None
        self.action = action

    def schedule(self, delay, target):
        assert self.action
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(
            delay.total_seconds(),
            self.action,
            args=[target])
        self.timer.start()

    def stop(self):
        if self.timer:
            self.timer.cancel()

    def __repr__(self):
        return 'DeskTimer(timer={}, action={})'.format(
            self.timer, self.action)
