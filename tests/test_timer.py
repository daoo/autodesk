from autodesk.timer import Timer
from datetime import timedelta
from unittest.mock import patch, Mock
import logging
import unittest


class TestTimer(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        loop_patcher = patch(
            'asyncio.AbstractEventLoop', autospec=True)
        self.loop = loop_patcher.start()
        self.addCleanup(loop_patcher.stop)

        self.callback = Mock()
        self.timer = Timer(self.loop)

    def test_timer_schedule_call_later_called(self):
        self.timer.schedule(timedelta(seconds=10), self.callback)
        self.loop.call_later.assert_called_with(10.0, self.callback)

    def test_timer_schedule_old_timer_cancelled(self):
        self.loop.call_later.return_value = timer1 = Mock()
        self.timer.schedule(timedelta(seconds=10), self.callback)
        self.loop.call_later.return_value = timer2 = Mock()
        self.timer.schedule(timedelta(seconds=10), self.callback)
        timer1.cancel.assert_called_once()
        timer2.cancel.assert_not_called()

    def test_timer_cancel_cancels(self):
        self.loop.call_later.return_value = timer = Mock()
        self.timer.schedule(timedelta(seconds=10), self.callback)
        self.timer.cancel()
        timer.cancel.assert_called_once()
