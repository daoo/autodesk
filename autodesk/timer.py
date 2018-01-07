from datetime import datetime, timedelta
import asyncio
import autodesk.stats as stats

class AsyncTimer:
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.task = asyncio.ensure_future(self.run())

    async def run(self):
        await asyncio.sleep(self.timeout.total_seconds())
        await self.callback()

    def cancel(self):
        self.task.cancel()


class TimerFactory:
    def __init__(self, callback):
        self.callback = callback

    def start(self, timeout, state):
        return AsyncTimer(timeout, lambda: self.callback(state))


class Timer:
    def __init__(self, limits, model, factory):
        self.limits = limits
        self.model = model
        self.factory = factory
        self.timer = None

    def update(self, time):
        beginning = datetime.fromtimestamp(0)
        session_spans = self.model.get_session_spans(beginning, time)
        if not session_spans[-1].data.active():
            self.cancel()
            return

        desk_spans = self.model.get_desk_spans(beginning, time)
        desk = desk_spans[-1].data
        active_time = stats.compute_active_time(session_spans, desk_spans)
        limit = desk.test(*self.limits)
        delay = max(timedelta(0), limit - active_time)

        self.timer = self.factory.start(delay, desk.next())

    def cancel(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None
