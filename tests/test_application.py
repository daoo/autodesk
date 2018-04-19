from autodesk.application import Application, Operation
from autodesk.model import Active, Inactive, Down, Up
from autodesk.spans import Event
from datetime import date, datetime, time, timedelta
from unittest.mock import patch, ANY
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

        self.model.get_session_state.return_value = Inactive()
        self.model.get_desk_state.return_value = Down()
        self.model.get_active_time.return_value = timedelta(seconds=0)
        self.operation.allowed.return_value = True

        self.application = Application(
            self.model,
            self.timer,
            self.hardware,
            self.operation,
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
        self.operation.allowed.return_value = False
        self.application.init()
        self.timer.cancel.assert_not_called()
        self.timer.schedule.assert_not_called()

    def test_init_inactive_operation_allowed_timer_not_scheduled(self):
        self.model.get_session_state.return_value = Inactive()
        self.operation.allowed.return_value = True
        self.model.get_active_time.return_value = timedelta(seconds=10)
        self.application.init()
        self.timer.schedule.assert_not_called()
        self.timer.cancel.assert_not_called()

    def test_init_active_operation_allowed_timer_scheduled(self):
        self.model.get_session_state.return_value = Active()
        self.operation.allowed.return_value = True
        self.model.get_active_time.return_value = timedelta(seconds=10)
        self.application.init()
        self.timer.schedule.assert_called_with(timedelta(seconds=10), ANY)
        self.timer.cancel.assert_not_called()

    def test_set_session_inactive_light_off(self):
        self.application.set_session(datetime(2018, 1, 1), Inactive())
        self.hardware.light.assert_called_with(Inactive())

    def test_set_session_active_light_on(self):
        self.application.set_session(datetime(2018, 1, 1), Active())
        self.hardware.light.assert_called_with(Active())

    def test_set_session_inactive_model_set_inactive(self):
        event = Event(datetime(2018, 1, 1), Inactive())
        self.application.set_session(event.index, event.data)
        self.model.set_session.assert_called_with(event)

    def test_set_session_active_timer_scheduled(self):
        event = Event(datetime(2018, 1, 1), Active())
        self.application.set_session(event.index, event.data)
        self.model.set_session.assert_called_with(event)

    def test_set_session_inactive_timer_cancelled(self):
        self.operation.allowed.return_value = True
        self.application.set_session(datetime(2018, 1, 1), Inactive())
        self.timer.schedule.assert_not_called()
        self.timer.cancel.assert_called_once()

    def test_set_desk_down_active_operation_allowed_hardware_down(self):
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
        self.model.get_session_state.return_value = Active()
        self.application.set_desk(datetime(2018, 1, 1), Down())
        self.timer.schedule.assert_called_with(timedelta(seconds=20), ANY)

    def test_set_desk_up_operation_allowed_timer_scheduled_10_seconds(self):
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
