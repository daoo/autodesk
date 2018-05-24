from autodesk.application import Application, ApplicationFactory
from autodesk.model import Active, Inactive, Down, Up
from autodesk.operation import Operation
from autodesk.spans import Event
from datetime import datetime, timedelta
import logging
import tests.utils as utils
import unittest
import unittest.mock


class TestApplication(utils.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        self.datetime = self.patch('autodesk.application.datetime')
        self.model = self.patch('autodesk.model.Model')
        self.timer = self.patch('autodesk.timer.Timer')
        self.hardware = self.patch('autodesk.hardware.noop.Noop')

        self.time_allowed = datetime(2018, 4, 23, 13, 0)
        self.time_denied = datetime(2018, 4, 23, 20, 0)
        self.now = self.datetime.now

        self.limits = (timedelta(seconds=20), timedelta(seconds=10))

        self.application = Application(
            self.model,
            self.timer,
            self.hardware,
            Operation(),
            self.limits)

    def test_init_inactive_light_off(self):
        self.model.get_session_state.return_value = Inactive()

        self.application.init()

        self.hardware.light.assert_called_with(Inactive())

    def test_init_active_light_on(self):
        self.model.get_session_state.return_value = Active()

        self.application.init()

        self.hardware.light.assert_called_with(Active())

    def test_init_active_operation_denied_timer_not_scheduled(self):
        self.model.get_session_state.return_value = Active()

        self.application.init()

        self.timer.cancel.assert_not_called()
        self.timer.schedule.assert_not_called()

    def test_init_inactive_operation_allowed_timer_not_scheduled(self):
        self.model.get_active_time.return_value = timedelta(seconds=10)
        self.model.get_session_state.return_value = Inactive()

        self.application.init()

        self.timer.schedule.assert_not_called()
        self.timer.cancel.assert_not_called()

    def test_init_active_operation_allowed_timer_scheduled(self):
        self.model.get_active_time.return_value = timedelta(seconds=10)
        self.model.get_desk_state.return_value = Down()
        self.model.get_session_state.return_value = Active()
        self.now.return_value = self.time_allowed

        self.application.init()

        self.timer.schedule.assert_called_with(timedelta(seconds=10),
                                               unittest.mock.ANY)
        self.timer.cancel.assert_not_called()

    def test_close_timer_cancelled(self):
        self.application.close()

        self.timer.cancel.assert_called_once()

    def test_close_hardware_closed(self):
        self.application.close()

        self.hardware.close.assert_called_once()

    def test_close_model_closed(self):
        self.application.close()

        self.model.close.assert_called_once()

    def test_get_active_time_returns_from_model(self):
        ret = self.application.get_active_time()

        self.assertEqual(ret, self.model.get_active_time.return_value)

    def test_get_session_state_returns_from_model(self):
        ret = self.application.get_session_state()

        self.assertEqual(ret, self.model.get_session_state.return_value)

    def test_get_desk_state_returns_from_model(self):
        ret = self.application.get_desk_state()

        self.assertEqual(ret, self.model.get_desk_state.return_value)

    @unittest.mock.patch('autodesk.application.stats', autospec=True)
    def test_get_daily_active_time_calls_stats_with_session_spans(self, stats):
        ret = self.application.get_daily_active_time()

        stats.compute_daily_active_time.assert_called_with(
            self.model.get_session_spans.return_value)
        self.assertEqual(ret, stats.compute_daily_active_time.return_value)

    def test_set_session_inactive_light_off(self):
        self.application.set_session(Inactive())

        self.hardware.light.assert_called_with(Inactive())

    def test_set_session_active_light_on(self):
        self.model.get_desk_state.return_value = Down()
        self.model.get_active_time.return_value = timedelta(0)
        self.application.set_session(Active())

        self.hardware.light.assert_called_with(Active())

    def test_set_session_inactive_model_set_inactive(self):
        self.now.return_value = self.time_allowed

        self.application.set_session(Inactive())

        self.model.set_session.assert_called_with(
            Event(self.time_allowed, Inactive()))

    def test_set_session_active_timer_scheduled(self):
        self.model.get_desk_state.return_value = Down()
        self.model.get_active_time.return_value = timedelta(0)
        self.now.return_value = self.time_allowed

        self.application.set_session(Active())

        self.model.set_session.assert_called_with(
            Event(self.time_allowed, Active()))

    def test_set_session_inactive_timer_cancelled(self):

        self.application.set_session(Inactive())

        self.timer.schedule.assert_not_called()
        self.timer.cancel.assert_called_once()

    def test_set_desk_down_active_operation_allowed_hardware_down(self):
        self.model.get_active_time.return_value = timedelta(0)
        self.model.get_session_state.return_value = Active()
        self.now.return_value = self.time_allowed

        self.application.set_desk(Down())

        self.hardware.desk.assert_called_with(Down())

    def test_set_desk_down_active_operation_denied_hardware_unchanged(self):
        self.model.get_session_state.return_value = Active()
        self.now.return_value = self.time_denied

        self.application.set_desk(Down())

        self.hardware.desk.assert_not_called()

    def test_set_desk_down_inactive_operation_allowed_hardware_unchanged(self):
        self.model.get_session_state.return_value = Inactive()
        self.now.return_value = self.time_allowed

        self.application.set_desk(Down())

        self.hardware.desk.assert_not_called()

    def test_set_desk_down_operation_allowed_timer_scheduled_20_seconds(self):
        self.model.get_active_time.return_value = timedelta(0)
        self.model.get_session_state.return_value = Active()
        self.now.return_value = self.time_allowed

        self.application.set_desk(Down())

        self.timer.schedule.assert_called_with(timedelta(seconds=20),
                                               unittest.mock.ANY)

    def test_set_desk_up_operation_allowed_timer_scheduled_10_seconds(self):
        self.model.get_active_time.return_value = timedelta(0)
        self.model.get_session_state.return_value = Active()
        self.now.return_value = self.time_allowed

        self.application.set_desk(Up())

        self.timer.schedule.assert_called_with(timedelta(seconds=10),
                                               unittest.mock.ANY)

    def test_set_desk_down_operation_denied_timer_not_scheduled(self):

        self.application.set_desk(Down())

        self.timer.cancel.assert_not_called()
        self.timer.schedule.assert_not_called()

    def test_set_desk_down_inactive_timer_not_scheduled(self):

        self.application.set_desk(Down())

        self.timer.cancel.assert_not_called()
        self.timer.schedule.assert_not_called()

    def test_set_session_timer_lambda_called_desk_down(self):
        self.model.get_active_time.return_value = timedelta(0)
        self.model.get_session_state.return_value = Active()
        self.model.get_desk_state.return_value = Down()
        self.now.return_value = self.time_allowed

        self.application.set_session(Active())
        self.timer.schedule.call_args[0][1]()

        self.hardware.desk.assert_called_with(Up())


class TestApplicationFactory(utils.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        self.model = self.patch('autodesk.application.Model')
        self.timer = self.patch('autodesk.application.Timer')
        self.hardware = self.patch('autodesk.application.create_hardware')
        self.operation = self.patch('autodesk.application.Operation')
        self.application = self.patch('autodesk.application.Application')

        self.limits = (timedelta(seconds=20), timedelta(seconds=10))
        self.database_path = "path"
        self.hardware_kind = "noop"
        self.delay = 5
        self.motor_pins = (1, 2)
        self.light_pin = 3

        self.factory = ApplicationFactory(
            self.database_path,
            self.hardware_kind,
            self.limits,
            self.delay,
            self.motor_pins,
            self.light_pin)

    def test_create_constructors_called(self):
        loop = unittest.mock.MagicMock()

        self.factory.create(loop)

        self.operation.assert_called_with()
        self.timer.assert_called_with(loop)
        self.hardware.assert_called_with(
            self.hardware_kind, self.delay, self.motor_pins, self.light_pin)
        self.application.assert_called_with(
            self.model.return_value,
            self.timer.return_value,
            self.hardware.return_value,
            self.operation.return_value,
            self.limits)
