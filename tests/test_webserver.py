from unittest.mock import MagicMock, patch
import autodesk.model as model
import unittest


class TestWebServer(unittest.TestCase):
    def setUp(self):
        # Importing hardware imports RPi which fails on non-raspberry
        # computers, mocking out hardware fixes the issue.
        import sys
        sys.modules['autodesk.hardware'] = MagicMock()
        self.addCleanup(sys.modules.pop, 'autodesk.hardware')

        self.datetime_patcher = patch(
            'autodesk.webserver.datetime',
            autospec=True)
        self.datetime = self.datetime_patcher.start()
        self.addCleanup(self.datetime_patcher.stop)
        self.now = self.datetime.now()

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

    @patch('autodesk.model.Snapshot', autospec=True)
    def test_webserver_index(self, snapshot):
        snapshot.get_active_time.return_value = '12:34:56'
        self.database.return_value.get_snapshot.return_value = snapshot
        rv = self.app.get('/')
        self.assertEqual(200, rv.status_code)
        self.assertTrue(b'12:34:56' in rv.data)

    @patch('autodesk.webserver.Stats', autospec=True)
    def test_webserver_get_session(self, stats):
        stats.compute_daily_active_time.return_value = [0] * 60*24
        rv = self.app.get('/api/get/session')
        self.assertEqual(200, rv.status_code)

    def test_webserver_set_desk_down(self):
        rv = self.app.get('/api/set/desk/0')
        self.controller.return_value.set_desk.assert_called_with(
            self.now, model.Down())
        self.assertEqual(200, rv.status_code)
        self.assertEqual(b'', rv.data)

    def test_webserver_set_desk_up(self):
        rv = self.app.get('/api/set/desk/1')
        self.controller.return_value.set_desk.assert_called_with(
            self.now, model.Up())
        self.assertEqual(200, rv.status_code)

    def test_webserver_set_desk_not_allowed(self):
        self.controller.return_value.set_desk.return_value = False
        rv = self.app.get('/api/set/desk/1')
        self.assertEqual(403, rv.status_code)

    def test_webserver_set_session_inactive(self):
        rv = self.app.get('/api/set/session/0')
        self.controller.return_value.set_session.assert_called_with(
            self.now, model.Inactive())
        self.assertEqual(200, rv.status_code)

    def test_webserver_set_session_active(self):
        rv = self.app.get('/api/set/session/1')
        self.controller.return_value.set_session.assert_called_with(
            self.now, model.Active())
        self.assertEqual(200, rv.status_code)
