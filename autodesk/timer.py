import threading


class Timer:
    def __init__(self, action):
        self.timer = None
        self.action = action

    def schedule(self, delay, target):
        assert self.action
        print('timer: scheduling {} in {}'.format(target, delay))
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(
            delay.total_seconds(),
            self.action,
            args=[target])
        self.timer.start()

    def stop(self):
        print('timer: stopping')
        if self.timer:
            self.timer.cancel()

    def __repr__(self):
        return 'DeskTimer(timer={}, action={})'.format(
            self.timer, self.action)
