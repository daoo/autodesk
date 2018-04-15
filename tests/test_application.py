from autodesk.application import Application
from autodesk.model import Active, Inactive, Down, Up
from autodesk.spans import Event
from datetime import datetime, timedelta
from unittest.mock import patch, ANY
import logging
import unittest


class TestApplication(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        model_patcher = patch('autodesk.model.Model', autospec=True)
        self.model = model_patcher.start()
        self.addCleanup(model_patcher.stop)

        timer_patcher = patch('autodesk.timer.Timer', autospec=True)
        self.timer = timer_patcher.start()
        self.addCleanup(timer_patcher.stop)

        hardware_patcher = patch('autodesk.hardware.noop.Noop', autospec=True)
        self.hardware = hardware_patcher.start()
        self.addCleanup(hardware_patcher.stop)

        self.limits = (timedelta(seconds=20), timedelta(seconds=10))

        self.model.get_session_state.return_value = Inactive()
        self.model.get_desk_state.return_value = Down()
        self.model.get_active_time.return_value = timedelta(seconds=0)

        self.application = Application(
            self.model,
            self.timer,
            self.hardware,
            self.limits)

    def test_init_session_inactive_light_off(self):
        self.model.get_session_state.return_value = Inactive()
        self.application.init()
        self.hardware.light.assert_called_with(Inactive())

    def test_init_session_active_light_on(self):
        self.model.get_session_state.return_value = Active()
        self.application.init()
        self.hardware.light.assert_called_with(Active())

    def test_init_session_inactive_timer_canceled(self):
        self.model.get_session_state.return_value = Inactive()
        self.application.init()
        self.timer.cancel.assert_called()
        self.timer.schedule.assert_not_called()

    def test_init_session_active_timer_scheduled(self):
        self.model.get_session_state.return_value = Active()
        self.model.get_active_time.return_value = timedelta(seconds=10)
        self.application.init()
        self.timer.schedule.assert_called_with(timedelta(seconds=10), ANY)
        self.timer.cancel.assert_not_called()

    def test_session_changed_inactivated_light_off(self):
        self.application.session_changed(Event(datetime(2018, 1, 1), Inactive()))
        self.hardware.light.assert_called_with(Inactive())

    def test_session_changed_activated_light_on(self):
        self.application.session_changed(Event(datetime(2018, 1, 1), Active()))
        self.hardware.light.assert_called_with(Active())

    def test_session_changed_inactivated_timer_cancelled(self):
        self.model.get_active_time.return_value = timedelta(seconds=10)
        self.application.session_changed(Event(datetime(2018, 1, 1), Inactive()))
        self.timer.cancel.assert_called()
        self.timer.schedule.assert_not_called()

    def test_session_changed_activated_timer_scheduled(self):
        self.model.get_active_time.return_value = timedelta(seconds=10)
        self.application.session_changed(Event(datetime(2018, 1, 1), Active()))
        self.timer.schedule.assert_called_with(timedelta(seconds=10), ANY)
        self.timer.cancel.assert_not_called()

    def test_desk_changed_down_desk_down(self):
        self.application.desk_changed(Event(datetime(2018, 1, 1), Down()))
        self.hardware.desk.assert_called_with(Down())

    def test_desk_changed_up_desk_up(self):
        self.application.desk_changed(Event(datetime(2018, 1, 1), Up()))
        self.hardware.desk.assert_called_with(Up())

    def test_desk_changed_down_timer_scheduled(self):
        self.model.get_session_state.return_value = Active()
        self.application.desk_changed(Event(datetime(2018, 1, 1), Down()))
        self.timer.schedule.assert_called_with(timedelta(seconds=20), ANY)

    def test_desk_changed_up_timer_scheduled(self):
        self.model.get_session_state.return_value = Active()
        self.application.desk_changed(Event(datetime(2018, 1, 1), Up()))
        self.timer.schedule.assert_called_with(timedelta(seconds=10), ANY)
        self.timer.cancel.assert_not_called()

    def test_desk_change_disallowed_timer_cancelled(self):
        self.application.desk_change_disallowed(Event(datetime(2018, 1, 1), Up()))
        self.timer.cancel.assert_called_once()
