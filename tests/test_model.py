from autodesk.model import Model, Up, Down, Active, Inactive
from autodesk.spans import Event, Span
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import autodesk.model as model
import logging
import unittest


class TestDown(unittest.TestCase):
    def test_next(self):
        self.assertEqual(Down().next(), Up())

    def test_test(self):
        self.assertEqual(Down().test(0, 1), 0)


class TestUp(unittest.TestCase):
    def test_next(self):
        self.assertEqual(Up().next(), Down())

    def test_test(self):
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


class TestModel(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        self.model = Model(':memory:')
        self.addCleanup(self.model.close)

    def test_empty_events(self):
        self.assertEqual(self.model.get_desk_events(), [])
        self.assertEqual(self.model.get_session_events(), [])

    def test_empty_spans(self):
        a = datetime.min
        b = datetime.max
        self.assertEqual(
            self.model.get_desk_spans(a, b),
            [Span(a, b, Down())])
        self.assertEqual(
            self.model.get_session_spans(a, b),
            [Span(a, b, Inactive())])

    def test_set_desk(self):
        event = Event(datetime(2017, 1, 1), Up())
        self.model.set_desk(event)
        self.assertEqual(self.model.get_desk_events(), [event])

    def test_set_session(self):
        event = Event(datetime(2017, 1, 1), Active())
        self.model.set_session(event)
        self.assertEqual(self.model.get_session_events(), [event])

    def test_get_desk_spans(self):
        a = datetime(2018, 1, 1)
        b = datetime(2018, 1, 2)
        c = datetime(2018, 1, 3)
        self.model.set_desk(Event(b, Up()))
        self.assertEqual(self.model.get_desk_spans(a, c), [
            Span(a, b, Down()),
            Span(b, c, Up())])

    def test_get_session_spans(self):
        a = datetime(2018, 1, 1)
        b = datetime(2018, 1, 2)
        c = datetime(2018, 1, 3)
        self.model.set_session(Event(b, Active()))
        self.assertEqual(self.model.get_session_spans(a, c), [
            Span(a, b, Inactive()),
            Span(b, c, Active())])

    def test_get_session_state_empty(self):
        self.assertEqual(self.model.get_session_state(), Inactive())

    def test_get_session_state_active(self):
        event = Event(datetime(2018, 1, 1), Active())
        self.model.set_session(event)
        self.assertEqual(self.model.get_session_state(), Active())

    def test_get_session_state_inactive(self):
        event = Event(datetime(2018, 1, 1), Inactive())
        self.model.set_session(event)
        self.assertEqual(self.model.get_session_state(), Inactive())

    def test_get_desk_state_empty(self):
        self.assertEqual(self.model.get_desk_state(), Down())

    def test_get_desk_state_up(self):
        event = Event(datetime(2018, 1, 1), Active())
        self.model.set_desk(event)
        self.assertEqual(self.model.get_desk_state(), Up())

    def test_get_desk_state_down(self):
        event = Event(datetime(2018, 1, 1), Inactive())
        self.model.set_desk(event)
        self.assertEqual(self.model.get_desk_state(), Down())

    def test_get_active_time_empty(self):
        self.assertEqual(
            self.model.get_active_time(datetime.min, datetime.max),
            None)

    def test_get_active_time_active_zero(self):
        event = Event(datetime(2018, 1, 1), Active())
        self.model.set_session(event)
        self.assertEqual(
            self.model.get_active_time(datetime.min, event.index),
            timedelta(0))

    def test_get_active_time_active_10_minutes(self):
        a = datetime(2018, 1, 1, 0, 0, 0)
        b = datetime(2018, 1, 1, 0, 10, 0)
        self.model.set_session(Event(a, Active()))
        self.assertEqual(
            self.model.get_active_time(datetime.min, b),
            timedelta(minutes=10))
