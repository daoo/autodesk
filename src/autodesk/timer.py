import asyncio
import logging
from collections.abc import Callable
from datetime import timedelta


class Timer:
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.logger = logging.getLogger("timer")
        self.loop = loop
        self.timer: asyncio.TimerHandle | None = None

    def schedule(self, delay: timedelta, callback: Callable[[], None]) -> None:
        self.logger.info("scheduling in %s", delay)
        if self.timer:
            self.timer.cancel()
        self.timer = self.loop.call_later(delay.total_seconds(), callback)

    def cancel(self) -> None:
        self.logger.info("cancelling")
        if self.timer:
            self.timer.cancel()
            self.timer = None
