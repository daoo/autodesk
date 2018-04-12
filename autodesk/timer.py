from datetime import datetime, timedelta
import asyncio
import autodesk.stats as stats
import logging


class TimerFactory:
    def __init__(self, loop, callback):
        assert loop
        self.loop = loop
        self.callback = callback

    def start(self, timeout, state):
        return self.loop.call_later(
            timeout.total_seconds(),
            self.callback,
            state)


class Timer:
    def __init__(self, limits, model, factory):
        self.logger = logging.getLogger('timer')
        self.limits = limits
        self.model = model
        self.factory = factory
        self.timer = None

    def update(self, time):
        if self.timer:
            self.timer.cancel()
            self.timer = None

        desk = self.model.get_desk_state()
        active_time = self.model.get_active_time(datetime.min, time)
        if active_time == None:
            self.logger.info('session is inactive, not scheduling')
            return
        limit = desk.test(*self.limits)
        delay = max(timedelta(0), limit - active_time)

        self.logger.info(
            'scheduling %s in %s',
            desk.next().test('down', 'up'),
            delay)
        self.timer = self.factory.start(delay, desk.next())

    def cancel(self):
        self.logger.info('cancling')
        if self.timer:
            self.timer.cancel()
            self.timer = None
