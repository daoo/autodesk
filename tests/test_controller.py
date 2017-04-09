from autodesk.controller import Controller, allow_desk_operation
from autodesk.spans import Event
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
            allow_desk_operation(datetime.combine(workday, time(8, 59, 0))))
        self.assertFalse(
            allow_desk_operation(datetime.combine(workday, time(17, 1, 0))))
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
        self.snapshot_patcher = patch(
            'autodesk.model.Snapshot', autospec=True)
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
        sys.modules['RPi.GPIO'] = MagicMock()

        self.snapshot = self.snapshot_patcher.start()
        self.addCleanup(self.snapshot_patcher.stop)
        self.database = self.database_patcher.start()
        self.addCleanup(self.database_patcher.stop)
        self.timer = self.timer_patcher.start()
        self.addCleanup(self.timer_patcher.stop)
        self.hardware = self.hardware_patcher.start()
        self.addCleanup(self.hardware_patcher.stop)

        self.database.get_snapshot.return_value = self.snapshot
        self.snapshot.get_active_time.return_value = timedelta(0)
        self.snapshot.get_latest_desk_state.return_value = model.Down()
        self.snapshot.get_latest_session_state.return_value = model.Inactive()

        limits = (timedelta(minutes=50), timedelta(minutes=10))
        self.controller = Controller(
            self.hardware, limits, self.timer, self.database)

    def tearDown(self):
        import sys
        del sys.modules['RPi']

    def test_update_timer(self):
        time0 = datetime.fromtimestamp(0)
        time1 = datetime(2017, 2, 13, 11, 0, 0)

        self.controller.update_timer(time1)
        self.database.get_snapshot.assert_called_with(
            initial=time0, final=time1)
        self.timer.stop.assert_called_once()

        self.snapshot.get_latest_session_state.return_value = model.Active()
        self.controller.update_timer(time1)
        self.database.get_snapshot.assert_called_with(
            initial=time0, final=time1)
        self.timer.set.assert_called_with(timedelta(seconds=3000), model.Up())

        self.snapshot.get_active_time.return_value = timedelta(seconds=1000)
        self.controller.update_timer(time1)
        self.database.get_snapshot.assert_called_with(
            initial=time0, final=time1)
        self.timer.set.assert_called_with(timedelta(seconds=2000), model.Up())

    def test_set_session_active(self):
        event = Event(datetime(2017, 2, 13, 12, 0, 0), model.Active())
        self.controller.set_session(event.index, event.data)
        self.database.insert_session_event.assert_called_with(event)

    def test_set_session_inactive(self):
        event = Event(datetime(2017, 2, 13, 13, 0, 0), model.Inactive())
        self.controller.set_session(event.index, event.data)
        self.database.insert_session_event.assert_called_with(event)

    def test_set_desk_up(self):
        self.snapshot.get_latest_session_state.return_value = model.Active()
        self.snapshot.get_latest_desk_state.return_value = model.Up()
        event = Event(datetime(2017, 2, 13, 12, 0, 0), model.Up())

        self.controller.set_desk(event.index, event.data)
        self.database.insert_desk_event.assert_called_with(event)
        self.hardware.setup.assert_called_once()
        self.hardware.go.assert_called_with(event.data)
        self.hardware.cleanup.assert_called_once()
        self.timer.stop.assert_not_called()
        self.timer.set.assert_called_with(timedelta(minutes=10), model.Down())

    def test_set_desk_down(self):
        self.snapshot.get_latest_session_state.return_value = model.Active()
        self.snapshot.get_latest_desk_state.return_value = model.Down()
        event = Event(datetime(2017, 2, 13, 12, 0, 0), model.Down())

        self.controller.set_desk(event.index, event.data)
        self.database.insert_desk_event.assert_called_with(event)
        self.hardware.setup.assert_called_once()
        self.hardware.go.assert_called_with(event.data)
        self.hardware.cleanup.assert_called_once()
        self.timer.stop.assert_not_called()
        self.timer.set.assert_called_with(timedelta(minutes=50), model.Up())

    def test_set_desk_disallow(self):
        event = Event(datetime(2017, 2, 13, 7, 0, 0), model.Down())
        self.controller.set_desk(event.index, event.data)
        self.database.insert_desk_event.assert_not_called()
        self.hardware.setup.assert_not_called()
        self.hardware.go.assert_not_called()
        self.hardware.cleanup.assert_not_called()
        self.timer.set.assert_not_called()
        self.timer.stop.assert_called_once()
