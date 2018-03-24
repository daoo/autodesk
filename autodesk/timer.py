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
        beginning = datetime.min
        session_spans = self.model.get_session_spans(beginning, time)
        if not session_spans[-1].data.active():
            self.cancel()
            return

        desk_spans = self.model.get_desk_spans(beginning, time)
        desk = desk_spans[-1].data
        active_time = stats.compute_active_time(session_spans, desk_spans)
        limit = desk.test(*self.limits)
        delay = max(timedelta(0), limit - active_time)

        self.logger.info(
            'next is %s in %s',
            desk.next().test('down', 'up'),
            delay)
        self.timer = self.factory.start(delay, desk.next())

    def cancel(self):
        self.logger.info('cancling')
        if self.timer:
            self.timer.cancel()
            self.timer = None
