from autodesk.application import Application, ApplicationFactory, Operation
from autodesk.model import Active, Inactive, Down, Up
from autodesk.spans import Event
from datetime import date, datetime, time, timedelta
from unittest.mock import patch, ANY, MagicMock
import logging
import unittest


class TestOperation(unittest.TestCase):
    def setUp(self):
        self.operation = Operation()

    def test_operation_allow_workday(self):
        monday = date(2017, 2, 13)
        tuesday = date(2017, 2, 14)
        wednesday = date(2017, 2, 15)
        thursday = date(2017, 2, 16)
        friday = date(2017, 2, 17)
        stroke = time(12, 0, 0)
        self.assertTrue(
            self.operation.allowed(datetime.combine(monday, stroke)))
        self.assertTrue(
            self.operation.allowed(datetime.combine(tuesday, stroke)))
        self.assertTrue(
            self.operation.allowed(datetime.combine(wednesday, stroke)))
        self.assertTrue(
            self.operation.allowed(datetime.combine(thursday, stroke)))
        self.assertTrue(
            self.operation.allowed(datetime.combine(friday, stroke)))

    def test_operation_disallow_night_time(self):
        workday = datetime(2017, 2, 13)
        self.assertFalse(
            self.operation.allowed(datetime.combine(workday, time(7, 59, 0))))
        self.assertFalse(
            self.operation.allowed(datetime.combine(workday, time(18, 1, 0))))
        self.assertFalse(
            self.operation.allowed(datetime.combine(workday, time(23, 0, 0))))
        self.assertFalse(
            self.operation.allowed(datetime.combine(workday, time(3, 0, 0))))
        self.assertFalse(
            self.operation.allowed(datetime.combine(workday, time(6, 0, 0))))

    def test_operation_disallow_weekend(self):
        saturday = date(2017, 2, 18)
        sunday = date(2017, 2, 19)
        stroke = time(12, 0, 0)
        self.assertFalse(
            self.operation.allowed(datetime.combine(saturday, stroke)))
        self.assertFalse(
            self.operation.allowed(datetime.combine(sunday, stroke)))


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

        operation_patcher = patch(
            'autodesk.application.Operation', autospec=True)
        self.operation = operation_patcher.start()
        self.addCleanup(operation_patcher.stop)

        self.limits = (timedelta(seconds=20), timedelta(seconds=10))

        self.application = Application(
            self.model,
            self.timer,
            self.hardware,
            self.operation,
            self.limits)

    def test_init_inactive_light_off(self):
        self.model.get_session_state.return_value = Inactive()
        self.operation.allowed.return_value = False

        self.application.init(datetime(2018, 1, 1))

        self.hardware.light.assert_called_with(Inactive())

    def test_init_active_light_on(self):
        self.model.get_session_state.return_value = Active()
        self.operation.allowed.return_value = False

        self.application.init(datetime(2018, 1, 1))

        self.hardware.light.assert_called_with(Active())

    def test_init_active_operation_denied_timer_not_scheduled(self):
        self.model.get_session_state.return_value = Active()
        self.operation.allowed.return_value = False

        self.application.init(datetime(2018, 1, 1))

        self.timer.cancel.assert_not_called()
        self.timer.schedule.assert_not_called()

    def test_init_inactive_operation_allowed_timer_not_scheduled(self):
        self.model.get_active_time.return_value = timedelta(seconds=10)
        self.model.get_session_state.return_value = Inactive()
        self.operation.allowed.return_value = True

        self.application.init(datetime(2018, 1, 1))

        self.timer.schedule.assert_not_called()
        self.timer.cancel.assert_not_called()

    def test_init_active_operation_allowed_timer_scheduled(self):
        self.model.get_active_time.return_value = timedelta(seconds=10)
        self.model.get_desk_state.return_value = Down()
        self.model.get_session_state.return_value = Active()
        self.operation.allowed.return_value = True

        self.application.init(datetime(2018, 1, 1))

        self.timer.schedule.assert_called_with(timedelta(seconds=10), ANY)
        self.timer.cancel.assert_not_called()

    def test_init_operation_allow_called_with_input(self):
        self.model.get_active_time.return_value = timedelta(0)
        self.model.get_session_state.return_value = Active()
        self.operation.allowed.return_value = False

        self.application.init(datetime(2018, 1, 1))

        self.operation.allowed.assert_called_with(datetime(2018, 1, 1))

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
        ret = self.application.get_active_time(1, 2)

        self.assertEqual(ret, self.model.get_active_time.return_value)

    def test_get_session_state_returns_from_model(self):
        ret = self.application.get_session_state()

        self.assertEqual(ret, self.model.get_session_state.return_value)

    def test_get_desk_state_returns_from_model(self):
        ret = self.application.get_desk_state()

        self.assertEqual(ret, self.model.get_desk_state.return_value)

    @patch('autodesk.application.stats', autospec=True)
    def test_get_daily_active_time_calls_stats_with_session_spans(self, stats):
        ret = self.application.get_daily_active_time(
            datetime.min, datetime(2018, 1, 1))

        stats.compute_daily_active_time.assert_called_with(
            self.model.get_session_spans.return_value)
        self.assertEqual(ret, stats.compute_daily_active_time.return_value)

    def test_set_session_inactive_light_off(self):
        self.application.set_session(datetime(2018, 1, 1), Inactive())

        self.hardware.light.assert_called_with(Inactive())

    def test_set_session_active_light_on(self):
        self.model.get_desk_state.return_value = Down()
        self.model.get_active_time.return_value = timedelta(0)
        self.application.set_session(datetime(2018, 1, 1), Active())

        self.hardware.light.assert_called_with(Active())

    def test_set_session_inactive_model_set_inactive(self):
        event = Event(datetime(2018, 1, 1), Inactive())

        self.application.set_session(event.index, event.data)

        self.model.set_session.assert_called_with(event)

    def test_set_session_active_timer_scheduled(self):
        self.model.get_desk_state.return_value = Down()
        self.model.get_active_time.return_value = timedelta(0)
        event = Event(datetime(2018, 1, 1), Active())

        self.application.set_session(event.index, event.data)

        self.model.set_session.assert_called_with(event)

    def test_set_session_inactive_timer_cancelled(self):
        self.operation.allowed.return_value = True

        self.application.set_session(datetime(2018, 1, 1), Inactive())

        self.timer.schedule.assert_not_called()
        self.timer.cancel.assert_called_once()

    def test_set_desk_down_active_operation_allowed_hardware_down(self):
        self.model.get_active_time.return_value = timedelta(0)
        self.model.get_session_state.return_value = Active()
        self.operation.allowed.return_value = True

        self.application.set_desk(datetime(2018, 4, 16, 10, 0, 0), Down())

        self.hardware.desk.assert_called_with(Down())

    def test_set_desk_down_operation_denied_hardware_unchanged(self):
        self.model.get_session_state.return_value = Active()
        self.operation.allowed.return_value = False

        self.application.set_desk(datetime(2018, 4, 16, 10, 0, 0), Down())

        self.hardware.desk.assert_not_called()

    def test_set_desk_down_inactive_hardware_unchanged(self):
        self.model.get_session_state.return_value = Inactive()
        self.operation.allowed.return_value = True

        self.application.set_desk(datetime(2018, 4, 16, 10, 0, 0), Down())

        self.hardware.desk.assert_not_called()

    def test_set_desk_down_operation_allowed_timer_scheduled_20_seconds(self):
        self.model.get_active_time.return_value = timedelta(0)
        self.model.get_session_state.return_value = Active()
        self.operation.allowed.return_value = True

        self.application.set_desk(datetime(2018, 1, 1), Down())

        self.timer.schedule.assert_called_with(timedelta(seconds=20), ANY)

    def test_set_desk_up_operation_allowed_timer_scheduled_10_seconds(self):
        self.model.get_active_time.return_value = timedelta(0)
        self.model.get_session_state.return_value = Active()
        self.operation.allowed.return_value = True

        self.application.set_desk(datetime(2018, 1, 1), Up())

        self.timer.schedule.assert_called_with(timedelta(seconds=10), ANY)

    def test_set_desk_down_operation_denied_timer_not_scheduled(self):
        self.operation.allowed.return_value = False

        self.application.set_desk(datetime(2018, 1, 1), Down())

        self.timer.cancel.assert_not_called()
        self.timer.schedule.assert_not_called()

    def test_set_desk_down_inactive_timer_not_scheduled(self):
        self.operation.allowed.return_value = False

        self.application.set_desk(datetime(2018, 1, 1), Down())

        self.timer.cancel.assert_not_called()
        self.timer.schedule.assert_not_called()

    @patch('autodesk.application.datetime', autospec=True)
    def test_set_session_timer_lambda_called_desk_down(self, datetime_mock):
        self.operation.allowed.return_value = True
        self.model.get_active_time.return_value = timedelta(0)
        self.model.get_session_state.return_value = Active()
        self.model.get_desk_state.return_value = Down()
        datetime_mock.now.return_value = datetime(2018, 4, 19, 12, 0)

        self.application.set_session(datetime(2018, 1, 1), Active())
        self.timer.schedule.call_args[0][1]()

        self.hardware.desk.assert_called_with(Up())


class TestApplicationFactory(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        model_patcher = patch('autodesk.application.Model', autospec=True)
        self.model = model_patcher.start()
        self.addCleanup(model_patcher.stop)

        timer_patcher = patch('autodesk.application.Timer', autospec=True)
        self.timer = timer_patcher.start()
        self.addCleanup(timer_patcher.stop)

        hardware_patcher = patch('autodesk.application.create_hardware',
                                 autospec=True)
        self.create_hardware = hardware_patcher.start()
        self.addCleanup(hardware_patcher.stop)

        operation_patcher = patch('autodesk.application.Operation',
                                  autospec=True)
        self.operation = operation_patcher.start()
        self.addCleanup(operation_patcher.stop)

        application_patcher = patch('autodesk.application.Application',
                                    autospec=True)
        self.application = application_patcher.start()
        self.addCleanup(application_patcher.stop)

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
        loop = MagicMock()

        self.factory.create(loop)

        self.operation.assert_called_with()
        self.timer.assert_called_with(loop)
        self.create_hardware.assert_called_with(
            self.hardware_kind, self.delay, self.motor_pins, self.light_pin)
        self.application.assert_called_with(
            self.model.return_value,
            self.timer.return_value,
            self.create_hardware.return_value,
            self.operation.return_value,
            self.limits)
