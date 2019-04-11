from aiohttp.test_utils import unittest_run_loop
from autodesk.model import Down, Up, Inactive, Active
from datetime import timedelta
import autodesk.server as server
import logging
import tests.utils as utils


class TestServer(utils.AioHTTPTestCase):
    async def get_application(self):
        logging.disable(logging.CRITICAL)

        factory = self.patch('autodesk.application.ApplicationFactory')
        self.application = self.patch('autodesk.application.Application')

        factory.create.return_value = self.application

        return server.setup_app(factory)

    @unittest_run_loop
    async def test_setup(self):
        self.application.init.assert_called_with()

    @unittest_run_loop
    async def test_index(self):
        self.application.get_active_time.return_value = timedelta(
            hours=12, minutes=34, seconds=56)
        self.application.get_session_state.return_value = Inactive()
        self.application.get_desk_state.return_value = Down()
        response = await self.client.get('/')
        self.assertEqual(200, response.status)
        expected = \
            'Currently <b>inactive</b> with ' + \
            'desk <b>down</b> for <b>12:34:56</b>.'
        self.assertTrue(expected in await response.text())

    @unittest_run_loop
    async def test_get_sessions_empty_values_are_zero(self):
        self.application.get_daily_active_time.return_value = \
            [0.0] * 7 * 24 * 60

        def all_zero(json):
            return all(all(obj['value'] == 0 for obj in day) for day in json)

        response = await self.client.get('/api/sessions.json')

        self.assertEqual(200, response.status)
        self.assertTrue(all_zero(await response.json()))

    @unittest_run_loop
    async def test_get_desk(self):
        self.application.get_desk_state.return_value = Down()
        response = await self.client.get('/api/desk')
        self.assertEqual('0', await response.text())

        self.application.get_desk_state.return_value = Up()
        response = await self.client.get('/api/desk')
        self.assertEqual('1', await response.text())

    @unittest_run_loop
    async def test_set_desk_down(self):
        response = await self.client.put('/api/desk', data=b'0')
        self.assertEqual(200, response.status)
        self.application.set_desk.assert_called_with(Down())

    @unittest_run_loop
    async def test_set_desk_up(self):
        response = await self.client.put('/api/desk', data=b'1')
        self.assertEqual(200, response.status)
        self.application.set_desk.assert_called_with(Up())

    @unittest_run_loop
    async def test_set_desk_not_allowed(self):
        self.application.set_desk.return_value = False
        response = await self.client.put('/api/desk', data=b'1')
        self.assertEqual(403, response.status)

    @unittest_run_loop
    async def test_get_session(self):
        self.application.get_session_state.return_value = Inactive()
        response = await self.client.get('/api/session')
        self.assertEqual('0', await response.text())

        self.application.get_session_state.return_value = Active()
        response = await self.client.get('/api/session')
        self.assertEqual('1', await response.text())

    @unittest_run_loop
    async def test_set_session_inactive(self):
        response = await self.client.put('/api/session', data=b'0')
        self.application.set_session.assert_called_with(Inactive())
        self.assertEqual(200, response.status)

    @unittest_run_loop
    async def test_set_session_active(self):
        response = await self.client.put('/api/session', data=b'1')
        self.application.set_session.assert_called_with(Active())
        self.assertEqual(200, response.status)
