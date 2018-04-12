from autodesk.model import Down, Up, Inactive, Active
from autodesk.spans import Span
from autodesk.timer import Timer, TimerFactory
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import logging
import unittest


class TestTimerFactor(unittest.TestCase):
    def setUp(self):
        self.loop = MagicMock()
        self.callback = MagicMock()
        self.factory = TimerFactory(self.loop, self.callback)

    def test_timer_factory_start(self):
        self.factory.start(timedelta(seconds=5), True)
        self.loop.call_later.assert_called_with(5, self.callback, True)


class TestTimer(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        limits = (timedelta(minutes=50), timedelta(minutes=10))

        factory_patcher = patch(
            'autodesk.timer.TimerFactory', autospec=True)
        self.factory = factory_patcher.start()
        self.addCleanup(factory_patcher.stop)

        model_patcher = patch(
            'autodesk.model.Model', autospec=True)
        self.model = model_patcher.start()
        self.addCleanup(model_patcher.stop)

        self.beginning = datetime.min
        self.now = datetime(2017, 4, 14, 10, 0, 0)

        self.timer = Timer(limits, self.model, self.factory)

    def test_timer_update_inactive(self):
        self.model.get_active_time.return_value = None
        self.model.get_desk_state.return_value = Down()
        self.timer.update(self.now)
        self.factory.start.assert_not_called()

    def test_timer_update_active(self):
        self.model.get_active_time.return_value = timedelta(minutes=0)
        self.model.get_desk_state.return_value = Down()
        self.timer.update(self.now)
        self.factory.start.assert_called_with(timedelta(minutes=50), Up())

    def test_timer_update_active_with_duration(self):
        self.model.get_active_time.return_value = timedelta(minutes=10)
        self.model.get_desk_state.return_value = Down()
        self.timer.update(self.now)
        self.factory.start.assert_called_with(timedelta(minutes=40), Up())

    def test_timer_cancel(self):
        self.model.get_active_time.return_value = timedelta(minutes=0)
        self.model.get_desk_state.return_value = Down()
        self.timer.update(self.now)
        self.timer.cancel()
        self.factory.start.return_value.cancel.assert_called_once()

    def test_timer_update_cancels_old_timer(self):
        self.model.get_desk_state.return_value = Down()

        self.model.get_active_time.return_value = timedelta(minutes=0)
        mock1 = MagicMock()
        self.factory.start.return_value = mock1
        self.timer.update(self.now)

        self.model.get_active_time.return_value = timedelta(minutes=10)
        mock2 = MagicMock()
        self.factory.start.return_value = mock2
        self.timer.update(self.now)

        mock1.cancel.assert_called_once()
