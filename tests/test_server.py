from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from autodesk.spans import Event, Span
from datetime import timedelta
from unittest.mock import patch, MagicMock
import autodesk.model as model
import autodesk.server as server
import logging


class TestServer(AioHTTPTestCase):
    async def get_application(self):
        logging.disable(logging.CRITICAL)

        datetime_patcher = patch(
            'autodesk.server.datetime', autospec=True)
        datetime = datetime_patcher.start()
        self.addCleanup(datetime_patcher.stop)
        self.now = datetime.now()

        model_patcher = patch(
            'autodesk.model.Model', autospec=True)
        self.model = model_patcher.start()
        self.addCleanup(model_patcher.stop)

        app = server.setup_app(None)

        app.on_cleanup.clear()
        app.on_startup.clear()

        app['model'] = self.model

        return app

    @unittest_run_loop
    async def test_server_index(self):
        self.model.get_active_time.return_value = timedelta(hours=12, minutes=34, seconds=56)
        self.model.get_session_state.return_value = model.Inactive()
        self.model.get_desk_state.return_value = model.Down()
        response = await self.client.get('/')
        self.assertEqual(200, response.status)
        str = 'Currently inactive with desk down for 12:34:56'
        self.assertTrue(str in await response.text())

    @unittest_run_loop
    async def test_server_get_sessions(self):
        response = await self.client.get('/api/sessions.json')
        self.assertEqual(200, response.status)

    @unittest_run_loop
    async def test_server_get_desk(self):
        self.model.get_desk_state.return_value = model.Down()
        response = await self.client.get('/api/desk')
        self.assertEqual('0', await response.text())

        self.model.get_desk_state.return_value = model.Up()
        response = await self.client.get('/api/desk')
        self.assertEqual('1', await response.text())

    @unittest_run_loop
    async def test_server_set_desk_down(self):
        response = await self.client.put('/api/desk', data=b'0')
        self.assertEqual(200, response.status)
        self.model.set_desk.assert_called_with(
            Event(self.now, model.Down()))

    @unittest_run_loop
    async def test_server_set_desk_up(self):
        response = await self.client.put('/api/desk', data=b'1')
        self.assertEqual(200, response.status)
        self.model.set_desk.assert_called_with(
            Event(self.now, model.Up()))

    @unittest_run_loop
    async def test_server_set_desk_not_allowed(self):
        self.model.set_desk.return_value = False
        response = await self.client.put('/api/desk', data=b'1')
        self.assertEqual(403, response.status)

    @unittest_run_loop
    async def test_server_get_session(self):
        self.model.get_session_state.return_value = model.Inactive()
        response = await self.client.get('/api/session')
        self.assertEqual('0', await response.text())

        self.model.get_session_state.return_value = model.Active()
        response = await self.client.get('/api/session')
        self.assertEqual('1', await response.text())

    @unittest_run_loop
    async def test_server_set_session_inactive(self):
        response = await self.client.put('/api/session', data=b'0')
        self.model.set_session.assert_called_with(
            Event(self.now, model.Inactive()))
        self.assertEqual(200, response.status)

    @unittest_run_loop
    async def test_server_set_session_active(self):
        response = await self.client.put('/api/session', data=b'1')
        self.model.set_session.assert_called_with(
            Event(self.now, model.Active()))
        self.assertEqual(200, response.status)
