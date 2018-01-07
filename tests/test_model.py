from autodesk.model import Model, Up, Down, Active, Inactive
from autodesk.spans import Event, Span
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import autodesk.model as model
import tempfile
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


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = Model(':memory:')
        self.addCleanup(self.model.close)

    def test_model_empty_events(self):
        self.assertEqual(self.model.get_desk_events(), [])
        self.assertEqual(self.model.get_session_events(), [])

    def test_model_empty_spans(self):
        a = datetime.fromtimestamp(0)
        b = datetime.fromtimestamp(1)
        self.assertEqual(
            list(self.model.get_desk_spans(a, b)),
            [Span(a, b, Down())]
        )
        self.assertEqual(
            list(self.model.get_session_spans(a, b)),
            [Span(a, b, Inactive())]
        )

    def test_model_insert_desk(self):
        a = datetime(2017, 1, 1)
        b = datetime(2017, 1, 2)
        c = datetime(2017, 1, 3)

        event = Event(b, Up())
        self.model.insert_desk_event(event)
        events = self.model.get_desk_events()
        self.assertEqual(events, [event])

        spans = list(self.model.get_desk_spans(a, c))
        self.assertEqual(spans, [Span(a, b, Down()), Span(b, c, Up())])

    def test_model_insert_session(self):
        a = datetime(2017, 1, 1)
        b = datetime(2017, 1, 2)
        c = datetime(2017, 1, 3)

        event = Event(b, Active())
        self.model.insert_session_event(event)
        events = self.model.get_session_events()
        self.assertEqual(events, [event])

        spans = list(self.model.get_session_spans(a, c))
        self.assertEqual(spans, [Span(a, b, Inactive()), Span(b, c, Active())])
