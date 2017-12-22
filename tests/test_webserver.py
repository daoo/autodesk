from autodesk.spans import Span
from unittest.mock import patch
import autodesk.model as model
import unittest


class TestWebServer(unittest.TestCase):
    def setUp(self):
        self.datetime_patcher = patch(
            'autodesk.webserver.datetime',
            autospec=True)
        self.datetime = self.datetime_patcher.start()
        self.addCleanup(self.datetime_patcher.stop)
        self.now = self.datetime.now()

        self.hardware_patcher = patch(
            'autodesk.webserver.Hardware',
            autospec=True)
        self.hardware = self.hardware_patcher.start()
        self.addCleanup(self.hardware_patcher.stop)

        self.controller_patcher = patch(
            'autodesk.webserver.Controller',
            autospec=True)
        self.controller = self.controller_patcher.start()
        self.addCleanup(self.controller_patcher.stop)

        self.database_patcher = patch(
            'autodesk.webserver.Database',
            autospec=True)
        self.database = self.database_patcher.start()
        self.addCleanup(self.database_patcher.stop)

        from autodesk.webserver import app
        self.app = app.test_client()

    @patch('autodesk.webserver.stats.compute_active_time', autospec=True)
    def test_webserver_index(self, compute_active_time):
        compute_active_time.return_value = '12:34:56'
        rv = self.app.get('/')
        self.assertEqual(200, rv.status_code)
        self.assertTrue(b'12:34:56' in rv.data)

    @patch('autodesk.webserver.stats.compute_daily_active_time', autospec=True)
    def test_webserver_get_session(self, compute_daily_active_time):
        compute_daily_active_time.return_value = [0]
        rv = self.app.get('/api/sessions.json')
        self.assertEqual(200, rv.status_code)

    def test_webserver_get_desk(self):
        self.database.return_value.get_desk_spans.return_value = \
                [Span(0, 1, model.Down())]
        rv = self.app.get('/api/desk')
        self.assertEqual(b'0', rv.data)

        self.database.return_value.get_desk_spans.return_value = \
                [Span(0, 1, model.Up())]
        rv = self.app.get('/api/desk')
        self.assertEqual(b'1', rv.data)

    def test_webserver_set_desk_down(self):
        rv = self.app.put('/api/desk', data=b'0')
        self.controller.return_value.set_desk.assert_called_with(
            self.now, model.Down())
        self.assertEqual(200, rv.status_code)
        self.assertEqual(b'', rv.data)

    def test_webserver_set_desk_up(self):
        rv = self.app.put('/api/desk', data=b'1')
        self.controller.return_value.set_desk.assert_called_with(
            self.now, model.Up())
        self.assertEqual(200, rv.status_code)

    def test_webserver_set_desk_not_allowed(self):
        self.controller.return_value.set_desk.return_value = False
        rv = self.app.put('/api/desk', data=b'1')
        self.assertEqual(403, rv.status_code)

    def test_webserver_get_session(self):
        self.database.return_value.get_session_spans.return_value = \
                [Span(0, 1, model.Inactive())]
        rv = self.app.get('/api/session')
        self.assertEqual(b'0', rv.data)

        self.database.return_value.get_session_spans.return_value = \
                [Span(0, 1, model.Active())]
        rv = self.app.get('/api/session')
        self.assertEqual(b'1', rv.data)

    def test_webserver_set_session_inactive(self):
        rv = self.app.put('/api/session', data=b'0')
        self.controller.return_value.set_session.assert_called_with(
            self.now, model.Inactive())
        self.assertEqual(200, rv.status_code)

    def test_webserver_set_session_active(self):
        rv = self.app.put('/api/session', data=b'1')
        self.controller.return_value.set_session.assert_called_with(
            self.now, model.Active())
        self.assertEqual(200, rv.status_code)

    def test_webserver_update_timer(self):
        rv = self.app.get('/api/timer/update')
        self.controller.return_value.update_timer.assert_called_with(self.now)
        self.assertEqual(200, rv.status_code)
