from autodesk.spans import Span
from unittest.mock import patch
import autodesk.model as model
import unittest


class TestWebServer(unittest.TestCase):
    def setUp(self):
        datetime_patcher = patch(
            'autodesk.webserver.datetime', autospec=True)
        datetime = datetime_patcher.start()
        self.addCleanup(datetime_patcher.stop)
        self.now = datetime.now()

        hardware_patcher = patch(
            'autodesk.webserver.Hardware', autospec=True)
        hardware = hardware_patcher.start()
        self.addCleanup(hardware_patcher.stop)

        timer_patcher = patch(
            'autodesk.webserver.Timer', autospec=True)
        self.timer = timer_patcher.start()
        self.addCleanup(timer_patcher.stop)

        controller_patcher = patch(
            'autodesk.webserver.Controller', autospec=True)
        self.controller = controller_patcher.start()
        self.addCleanup(controller_patcher.stop)

        database_patcher = patch(
            'autodesk.webserver.Database', autospec=True)
        self.database = database_patcher.start()
        self.addCleanup(database_patcher.stop)

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
        self.timer.return_value.update.assert_called_with(self.now)
        self.assertEqual(200, rv.status_code)
