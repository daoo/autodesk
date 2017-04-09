from autodesk.model import Database, Up, Down, Active, Inactive
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


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.database_file = tempfile.NamedTemporaryFile()
        self.database = Database(self.database_file.name)
        self.addCleanup(self.database.close)
        self.addCleanup(self.database_file.close)

    def test_database_empty_events(self):
        self.assertEqual(self.database.get_desk_events(), [])
        self.assertEqual(self.database.get_session_events(), [])

    def test_database_empty_spans(self):
        a = datetime.fromtimestamp(0)
        b = datetime.fromtimestamp(1)
        self.assertEqual(
            list(self.database.get_desk_spans(a, b)),
            [Span(a, b, Down())]
        )
        self.assertEqual(
            list(self.database.get_session_spans(a, b)),
            [Span(a, b, Inactive())]
        )

    def test_database_insert_desk(self):
        a = datetime(2017, 1, 1)
        b = datetime(2017, 1, 2)
        c = datetime(2017, 1, 3)

        event = Event(b, Up())
        self.database.insert_desk_event(event)
        events = self.database.get_desk_events()
        self.assertEqual(events, [event])

        spans = list(self.database.get_desk_spans(a, c))
        self.assertEqual(spans, [Span(a, b, Down()), Span(b, c, Up())])

    def test_database_insert_session(self):
        a = datetime(2017, 1, 1)
        b = datetime(2017, 1, 2)
        c = datetime(2017, 1, 3)

        event = Event(b, Active())
        self.database.insert_session_event(event)
        events = self.database.get_session_events()
        self.assertEqual(events, [event])

        spans = list(self.database.get_session_spans(a, c))
        self.assertEqual(spans, [Span(a, b, Inactive()), Span(b, c, Active())])

    def test_snapshot_empty(self):
        a = datetime(2017, 1, 1)
        b = datetime(2017, 1, 2)
        snapshot = self.database.get_snapshot(a, b)

        self.assertEqual(snapshot.get_active_time(), timedelta(0))
        self.assertEqual(snapshot.get_latest_session_state(), Inactive())
        self.assertEqual(snapshot.get_latest_desk_state(), Down())

    def test_snapshot_example(self):
        a = datetime(2017, 1, 1, 0, 0, 0)
        b = datetime(2017, 1, 1, 0, 10, 0)
        c = datetime(2017, 1, 1, 0, 20, 0)
        d = datetime(2017, 1, 1, 0, 30, 0)
        e = datetime(2017, 1, 1, 0, 40, 0)
        session_events = [Event(b, Active()), Event(d, Inactive())]
        desk_events = [Event(c, Up())]
        for event in session_events:
            self.database.insert_session_event(event)
        for event in desk_events:
            self.database.insert_desk_event(event)

        snapshot = self.database.get_snapshot(a, e)
        self.assertEqual(snapshot.get_active_time(), timedelta(minutes=10))
        self.assertEqual(snapshot.get_latest_session_state(), Inactive())
        self.assertEqual(snapshot.get_latest_desk_state(), Up())
