from autodesk.controller import Controller, Operation
from autodesk.spans import Event
from datetime import date, datetime, time
from unittest.mock import MagicMock, patch
import autodesk.model as model
import unittest


class TestOperation(unittest.TestCase):
    def test_operation_allow_workday(self):
        monday = date(2017, 2, 13)
        tuesday = date(2017, 2, 14)
        wednesday = date(2017, 2, 15)
        thursday = date(2017, 2, 16)
        friday = date(2017, 2, 17)
        stroke = time(12, 0, 0)
        self.assertTrue(
            Operation.allow(datetime.combine(monday, stroke)))
        self.assertTrue(
            Operation.allow(datetime.combine(tuesday, stroke)))
        self.assertTrue(
            Operation.allow(datetime.combine(wednesday, stroke)))
        self.assertTrue(
            Operation.allow(datetime.combine(thursday, stroke)))
        self.assertTrue(
            Operation.allow(datetime.combine(friday, stroke)))

    def test_operation_disallow_night_time(self):
        workday = datetime(2017, 2, 13)
        self.assertFalse(
            Operation.allow(datetime.combine(workday, time(7, 59, 0))))
        self.assertFalse(
            Operation.allow(datetime.combine(workday, time(18, 1, 0))))
        self.assertFalse(
            Operation.allow(datetime.combine(workday, time(23, 0, 0))))
        self.assertFalse(
            Operation.allow(datetime.combine(workday, time(3, 0, 0))))
        self.assertFalse(
            Operation.allow(datetime.combine(workday, time(6, 0, 0))))

    def test_operation_disallow_weekend(self):
        saturday = date(2017, 2, 18)
        sunday = date(2017, 2, 19)
        stroke = time(12, 0, 0)
        self.assertFalse(
            Operation.allow(datetime.combine(saturday, stroke)))
        self.assertFalse(
            Operation.allow(datetime.combine(sunday, stroke)))


class TestController(unittest.TestCase):
    def setUp(self):
        database_patcher = patch(
            'autodesk.model.Database', autospec=True)
        self.database = database_patcher.start()
        self.addCleanup(database_patcher.stop)

        hardware_patcher = patch(
            'autodesk.hardware.Hardware', autospec=True)
        self.hardware = hardware_patcher.start()
        self.addCleanup(hardware_patcher.stop)

        self.controller = Controller(self.hardware, self.database)
        self.observer = MagicMock()
        self.controller.add_observer(self.observer)

    def test_controller_set_session_active(self):
        event = Event(datetime(2017, 2, 13, 12, 0, 0), model.Active())
        self.controller.set_session(event.index, event.data)
        self.database.insert_session_event.assert_called_with(event)
        self.hardware.light.assert_called_with(event.data)
        self.observer.session_changed.assert_called_with(event.index,
                                                         event.data)

    def test_controller_set_session_inactive(self):
        event = Event(datetime(2017, 2, 13, 13, 0, 0), model.Inactive())
        self.controller.set_session(event.index, event.data)
        self.database.insert_session_event.assert_called_with(event)
        self.hardware.light.assert_called_with(event.data)
        self.observer.session_changed.assert_called_with(event.index,
                                                         event.data)

    def test_controller_set_desk_up(self):
        event = Event(datetime(2017, 2, 13, 12, 0, 0), model.Up())
        self.controller.set_desk(event.index, event.data)
        self.database.insert_desk_event.assert_called_with(event)
        self.hardware.go.assert_called_with(event.data)
        self.observer.desk_changed.assert_called_with(event.index, event.data)

    def test_controller_set_desk_down(self):
        event = Event(datetime(2017, 2, 13, 12, 0, 0), model.Down())
        self.controller.set_desk(event.index, event.data)
        self.database.insert_desk_event.assert_called_with(event)
        self.hardware.go.assert_called_with(event.data)
        self.observer.desk_changed.assert_called_with(event.index, event.data)

    def test_controller_set_desk_disallow(self):
        event = Event(datetime(2017, 2, 13, 7, 0, 0), model.Down())
        self.controller.set_desk(event.index, event.data)
        self.database.insert_desk_event.assert_not_called()
        self.hardware.go.assert_not_called()
        self.observer.desk_change_disallowed.assert_called_with(event.index)
