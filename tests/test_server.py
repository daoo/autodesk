from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from autodesk.model import Down, Up, Inactive, Active
from datetime import timedelta
from unittest.mock import patch
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

        application_factory_patcher = patch(
            'autodesk.application.ApplicationFactory', autospec=True)
        application_factory = application_factory_patcher.start()
        self.addCleanup(application_factory_patcher.stop)
        self.application = application_factory.create.return_value

        return server.setup_app(application_factory)

    @unittest_run_loop
    async def test_server_index(self):
        self.application.get_active_time.return_value = timedelta(
            hours=12, minutes=34, seconds=56)
        self.application.get_session_state.return_value = Inactive()
        self.application.get_desk_state.return_value = Down()
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
        self.application.get_desk_state.return_value = Down()
        response = await self.client.get('/api/desk')
        self.assertEqual('0', await response.text())

        self.application.get_desk_state.return_value = Up()
        response = await self.client.get('/api/desk')
        self.assertEqual('1', await response.text())

    @unittest_run_loop
    async def test_server_set_desk_down(self):
        response = await self.client.put('/api/desk', data=b'0')
        self.assertEqual(200, response.status)
        self.application.set_desk.assert_called_with(self.now, Down())

    @unittest_run_loop
    async def test_server_set_desk_up(self):
        response = await self.client.put('/api/desk', data=b'1')
        self.assertEqual(200, response.status)
        self.application.set_desk.assert_called_with(self.now, Up())

    @unittest_run_loop
    async def test_server_set_desk_not_allowed(self):
        self.application.set_desk.return_value = False
        response = await self.client.put('/api/desk', data=b'1')
        self.assertEqual(403, response.status)

    @unittest_run_loop
    async def test_server_get_session(self):
        self.application.get_session_state.return_value = Inactive()
        response = await self.client.get('/api/session')
        self.assertEqual('0', await response.text())

        self.application.get_session_state.return_value = Active()
        response = await self.client.get('/api/session')
        self.assertEqual('1', await response.text())

    @unittest_run_loop
    async def test_server_set_session_inactive(self):
        response = await self.client.put('/api/session', data=b'0')
        self.application.set_session.assert_called_with(self.now, Inactive())
        self.assertEqual(200, response.status)

    @unittest_run_loop
    async def test_server_set_session_active(self):
        response = await self.client.put('/api/session', data=b'1')
        self.application.set_session.assert_called_with(self.now, Active())
        self.assertEqual(200, response.status)
