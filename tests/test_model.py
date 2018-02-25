from autodesk.model import Model, Operation, Up, Down, Active, Inactive
from autodesk.spans import Event, Span
from datetime import datetime, date, time
from unittest.mock import MagicMock, patch
import autodesk.model as model
import logging
import unittest


class TestDown(unittest.TestCase):
    def test_down_next(self):
        self.assertEqual(Down().next(), Up())

    def test_down_test(self):
        self.assertEqual(Down().test(0, 1), 0)


class TestUp(unittest.TestCase):
    def test_up_next(self):
        self.assertEqual(Up().next(), Down())

    def test_up_test(self):
        self.assertEqual(Up().test(0, 1), 1)


class TestFactoryMethods(unittest.TestCase):
    def test_session_from_int(self):
        self.assertEqual(model.session_from_int(0), Inactive())
        self.assertEqual(model.session_from_int(1), Active())
        self.assertRaises(ValueError, model.session_from_int, 2)

    def test_desk_from_int(self):
        self.assertEqual(model.desk_from_int(0), Down())
        self.assertEqual(model.desk_from_int(1), Up())
        self.assertRaises(ValueError, model.desk_from_int, 2)

    def test_event_from_row_incorrect(self):
        cursor = MagicMock()
        cursor.description = [['date'], ['foobar']]
        values = [0, 0]
        self.assertRaises(ValueError, model.event_from_row, cursor, values)


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
            self.operation.allow(datetime.combine(monday, stroke)))
        self.assertTrue(
            self.operation.allow(datetime.combine(tuesday, stroke)))
        self.assertTrue(
            self.operation.allow(datetime.combine(wednesday, stroke)))
        self.assertTrue(
            self.operation.allow(datetime.combine(thursday, stroke)))
        self.assertTrue(
            self.operation.allow(datetime.combine(friday, stroke)))

    def test_operation_disallow_night_time(self):
        workday = datetime(2017, 2, 13)
        self.assertFalse(
            self.operation.allow(datetime.combine(workday, time(7, 59, 0))))
        self.assertFalse(
            self.operation.allow(datetime.combine(workday, time(18, 1, 0))))
        self.assertFalse(
            self.operation.allow(datetime.combine(workday, time(23, 0, 0))))
        self.assertFalse(
            self.operation.allow(datetime.combine(workday, time(3, 0, 0))))
        self.assertFalse(
            self.operation.allow(datetime.combine(workday, time(6, 0, 0))))

    def test_operation_disallow_weekend(self):
        saturday = date(2017, 2, 18)
        sunday = date(2017, 2, 19)
        stroke = time(12, 0, 0)
        self.assertFalse(
            self.operation.allow(datetime.combine(saturday, stroke)))
        self.assertFalse(
            self.operation.allow(datetime.combine(sunday, stroke)))


class TestModel(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        operation_patcher = patch(
            'autodesk.model.Operation', autospec=True)
        self.operation = operation_patcher.start()
        self.addCleanup(operation_patcher.stop)

        self.model = Model(':memory:', self.operation)
        self.addCleanup(self.model.close)
        self.observer = MagicMock()
        self.model.add_observer(self.observer)

    def test_model_empty_events(self):
        self.assertEqual(self.model.get_desk_events(), [])
        self.assertEqual(self.model.get_session_events(), [])

    def test_model_empty_spans(self):
        a = datetime.fromtimestamp(0)
        b = datetime.fromtimestamp(1)
        self.assertEqual(
            self.model.get_desk_spans(a, b),
            [Span(a, b, Down())])
        self.assertEqual(
            self.model.get_session_spans(a, b),
            [Span(a, b, Inactive())])

    def test_model_set_desk(self):
        event = Event(datetime(2017, 1, 1), Up())
        self.model.set_desk(event)
        self.observer.desk_changed.assert_called_with(event)
        self.assertEqual(self.model.get_desk_events(), [event])

    def test_model_set_desk_disallowed(self):
        event = Event(datetime(2017, 1, 1), Up())
        self.operation.allow.return_value = False
        self.model.set_desk(event)
        self.observer.desk_change_disallowed.assert_called_with(event)
        self.assertEqual(self.model.get_desk_events(), [])

    def test_model_set_session(self):
        event = Event(datetime(2017, 1, 1), Active())
        self.model.set_session(event)
        self.observer.session_changed.assert_called_with(event)
        self.assertEqual(self.model.get_session_events(), [event])

    def test_model_get_desk_spans(self):
        a = datetime(2018, 1, 1)
        b = datetime(2018, 1, 2)
        c = datetime(2018, 1, 3)
        self.model.set_desk(Event(b, Up()))
        self.assertEqual(self.model.get_desk_spans(a, c), [
            Span(a, b, Down()),
            Span(b, c, Up())])

    def test_model_get_session_spans(self):
        a = datetime(2018, 1, 1)
        b = datetime(2018, 1, 2)
        c = datetime(2018, 1, 3)
        self.model.set_session(Event(b, Active()))
        self.assertEqual(self.model.get_session_spans(a, c), [
            Span(a, b, Inactive()),
            Span(b, c, Active())])
