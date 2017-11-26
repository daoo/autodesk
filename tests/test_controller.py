from autodesk.controller import Controller, allow_desk_operation
from autodesk.spans import Event, Span
from datetime import date, datetime, time, timedelta
from unittest.mock import MagicMock, patch
import autodesk.model as model
import unittest


class TestOperation(unittest.TestCase):
    def test_allow_operation_workday(self):
        monday = date(2017, 2, 13)
        tuesday = date(2017, 2, 14)
        wednesday = date(2017, 2, 15)
        thursday = date(2017, 2, 16)
        friday = date(2017, 2, 17)
        stroke = time(12, 0, 0)
        self.assertTrue(
            allow_desk_operation(datetime.combine(monday, stroke)))
        self.assertTrue(
            allow_desk_operation(datetime.combine(tuesday, stroke)))
        self.assertTrue(
            allow_desk_operation(datetime.combine(wednesday, stroke)))
        self.assertTrue(
            allow_desk_operation(datetime.combine(thursday, stroke)))
        self.assertTrue(
            allow_desk_operation(datetime.combine(friday, stroke)))

    def test_disallow_operation_night_time(self):
        workday = datetime(2017, 2, 13)
        self.assertFalse(
            allow_desk_operation(datetime.combine(workday, time(7, 59, 0))))
        self.assertFalse(
            allow_desk_operation(datetime.combine(workday, time(18, 1, 0))))
        self.assertFalse(
            allow_desk_operation(datetime.combine(workday, time(23, 0, 0))))
        self.assertFalse(
            allow_desk_operation(datetime.combine(workday, time(3, 0, 0))))
        self.assertFalse(
            allow_desk_operation(datetime.combine(workday, time(6, 0, 0))))

    def test_disallow_operation_weekend(self):
        saturday = date(2017, 2, 18)
        sunday = date(2017, 2, 19)
        stroke = time(12, 0, 0)
        self.assertFalse(
            allow_desk_operation(datetime.combine(saturday, stroke)))
        self.assertFalse(
            allow_desk_operation(datetime.combine(sunday, stroke)))


class TestController(unittest.TestCase):
    def setUp(self):
        self.database_patcher = patch(
            'autodesk.model.Database', autospec=True)
        self.timer_patcher = patch(
            'autodesk.timer.Timer', autospec=True)
        self.hardware_patcher = patch(
            'autodesk.hardware.Hardware', autospec=True)

        # Starting the patch will import hardware and thus try to import the
        # RPi modules which fails on non raspberry computers.
        import sys
        sys.modules['RPi'] = MagicMock()
        self.addCleanup(sys.modules.pop, 'RPi')
        sys.modules['RPi.GPIO'] = MagicMock()
        self.addCleanup(sys.modules.pop, 'RPi.GPIO')

        self.database = self.database_patcher.start()
        self.addCleanup(self.database_patcher.stop)
        self.timer = self.timer_patcher.start()
        self.addCleanup(self.timer_patcher.stop)
        self.hardware = self.hardware_patcher.start()
        self.addCleanup(self.hardware_patcher.stop)

        self.beginning = datetime.fromtimestamp(0)
        self.now = datetime(2017, 4, 14, 10, 0, 0)
        self.database.get_desk_spans.return_value = [
            Span(self.beginning, self.now, model.Down())
        ]
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, model.Inactive())
        ]

        limits = (timedelta(minutes=50), timedelta(minutes=10))
        self.controller = Controller(
            self.hardware, limits, self.timer, self.database)

    def test_update_timer_inactive(self):
        self.controller.update_timer(self.now)
        self.timer.stop.assert_called_once()
        self.database.get_desk_spans.assert_not_called()

    @patch('autodesk.controller.stats.compute_active_time', autospec=True)
    def test_update_timer_active(self, compute_active_time):
        compute_active_time.return_value = timedelta(0)
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, model.Active())
        ]
        self.controller.update_timer(self.now)
        self.timer.schedule.assert_called_with(
            timedelta(minutes=50), model.Up())

    @patch('autodesk.controller.stats.compute_active_time', autospec=True)
    def test_update_timer_active_duration(self, compute_active_time):
        compute_active_time.return_value = timedelta(minutes=10)
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, model.Active())
        ]
        self.controller.update_timer(self.now)
        self.timer.schedule.assert_called_with(
            timedelta(minutes=40), model.Up())

    def test_set_session_active(self):
        event = Event(datetime(2017, 2, 13, 12, 0, 0), model.Active())
        self.controller.set_session(event.index, event.data)
        self.database.insert_session_event.assert_called_with(event)
        self.hardware.setup.assert_called_once()
        self.hardware.light.assert_called_with(event.data)
        self.hardware.cleanup.assert_called_once()

    def test_set_session_inactive(self):
        event = Event(datetime(2017, 2, 13, 13, 0, 0), model.Inactive())
        self.controller.set_session(event.index, event.data)
        self.database.insert_session_event.assert_called_with(event)
        self.hardware.setup.assert_called_once()
        self.hardware.light.assert_called_with(event.data)
        self.hardware.cleanup.assert_called_once()

    @patch('autodesk.controller.stats.compute_active_time', autospec=True)
    def test_set_desk_up(self, compute_active_time):
        compute_active_time.return_value = timedelta(0)
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, model.Active())
        ]
        self.database.get_desk_spans.return_value = [
            Span(self.beginning, self.now, model.Up())
        ]
        event = Event(datetime(2017, 2, 13, 12, 0, 0), model.Up())

        self.controller.set_desk(event.index, event.data)
        self.database.insert_desk_event.assert_called_with(event)
        self.hardware.setup.assert_called_once()
        self.hardware.go.assert_called_with(event.data)
        self.hardware.cleanup.assert_called_once()
        self.timer.stop.assert_not_called()
        self.timer.schedule.assert_called_with(
            timedelta(minutes=10), model.Down())

    @patch('autodesk.controller.stats.compute_active_time', autospec=True)
    def test_set_desk_down(self, compute_active_time):
        compute_active_time.return_value = timedelta(0)
        self.database.get_session_spans.return_value = [
            Span(self.beginning, self.now, model.Active())
        ]
        self.database.get_desk_spans.return_value = [
            Span(self.beginning, self.now, model.Down())
        ]
        event = Event(datetime(2017, 2, 13, 12, 0, 0), model.Down())

        self.controller.set_desk(event.index, event.data)
        self.database.insert_desk_event.assert_called_with(event)
        self.hardware.setup.assert_called_once()
        self.hardware.go.assert_called_with(event.data)
        self.hardware.cleanup.assert_called_once()
        self.timer.stop.assert_not_called()
        self.timer.schedule.assert_called_with(
            timedelta(minutes=50), model.Up())

    def test_set_desk_disallow(self):
        event = Event(datetime(2017, 2, 13, 7, 0, 0), model.Down())
        self.controller.set_desk(event.index, event.data)
        self.database.insert_desk_event.assert_not_called()
        self.hardware.setup.assert_not_called()
        self.hardware.go.assert_not_called()
        self.hardware.cleanup.assert_not_called()
        self.timer.schedule.assert_not_called()
        self.timer.stop.assert_called_once()
