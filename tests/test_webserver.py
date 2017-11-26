from autodesk.spans import Span
from unittest.mock import patch
import autodesk.model as model
import msgpack
import unittest


class TestWebServer(unittest.TestCase):
    def setUp(self):
        self.datetime_patcher = patch(
            'autodesk.webserver.datetime',
            autospec=True)
        self.datetime = self.datetime_patcher.start()
        self.addCleanup(self.datetime_patcher.stop)
        self.now = self.datetime.now()

        self.socket_patcher = patch(
            'autodesk.webserver.Socket',
            autospec=True)
        self.socket = self.socket_patcher.start()
        self.addCleanup(self.socket_patcher.stop)

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
    def test_webserver_get_sessions(self, compute_daily_active_time):
        compute_daily_active_time.return_value = [0]
        rv = self.app.get('/api/sessions.json')
        self.assertEqual(200, rv.status_code)

    def test_webserver_get_desk(self):
        self.database.return_value.get_desk_spans.return_value = [
            Span(0, 1, model.Down())]
        rv = self.app.get('/api/desk')
        self.assertEqual(b'0', rv.data)

        self.database.return_value.get_desk_spans.return_value = [
            Span(0, 1, model.Up())]
        rv = self.app.get('/api/desk')
        self.assertEqual(b'1', rv.data)

    def test_webserver_set_desk_down(self):
        rv = self.app.put('/api/desk', data=b'0')
        self.socket.return_value.send.assert_called_with(
            msgpack.packb(['desk', 0]))
        self.assertEqual(200, rv.status_code)
        self.assertEqual(b'', rv.data)

    def test_webserver_set_desk_up(self):
        rv = self.app.put('/api/desk', data=b'1')
        self.socket.return_value.send.assert_called_with(
            msgpack.packb(['desk', 1]))
        self.assertEqual(200, rv.status_code)

    def test_webserver_get_session(self):
        self.database.return_value.get_session_spans.return_value = [
            Span(0, 1, model.Inactive())]
        rv = self.app.get('/api/session')
        self.assertEqual(b'0', rv.data)

        self.database.return_value.get_session_spans.return_value = [
            Span(0, 1, model.Active())]
        rv = self.app.get('/api/session')
        self.assertEqual(b'1', rv.data)

    def test_webserver_set_session_inactive(self):
        rv = self.app.put('/api/session', data=b'0')
        self.socket.return_value.send.assert_called_with(
            msgpack.packb(['session', 0]))
        self.assertEqual(200, rv.status_code)

    def test_webserver_set_session_active(self):
        rv = self.app.put('/api/session', data=b'1')
        self.socket.return_value.send.assert_called_with(
            msgpack.packb(['session', 1]))
        self.assertEqual(200, rv.status_code)

    def test_webserver_static(self):
        rv = self.app.get('/static/Chart.bundle.min.js')
        self.assertEqual(200, rv.status_code)
