from autodesk.timer import Timer
from datetime import timedelta
from unittest.mock import Mock
import logging
import tests.utils as utils


class TestTimer(utils.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        self.loop = self.patch('asyncio.AbstractEventLoop')
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

    def test_timer_not_running_cancel_nothing_happens(self):
        self.loop.call_later.return_value = timer = Mock()
        self.timer.cancel()
        timer.cancel.assert_not_called()
