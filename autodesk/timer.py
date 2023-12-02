import logging


class Timer:
    def __init__(self, loop):
        self.logger = logging.getLogger("timer")
        self.loop = loop
        self.timer = None

    def schedule(self, delay, callback):
        self.logger.info("scheduling in %s", delay)
        if self.timer:
            self.timer.cancel()
        self.timer = self.loop.call_later(delay.total_seconds(), callback)

    def cancel(self):
        self.logger.info("cancling")
        if self.timer:
            self.timer.cancel()
            self.timer = None
