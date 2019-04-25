from aiohttp.test_utils import unittest_run_loop
from autodesk.application import Application
from autodesk.hardware.noop import Noop
from autodesk.model import Down, Inactive, Active
from autodesk.operation import Operation
from autodesk.spans import Span
from datetime import datetime, timedelta
import autodesk.server as server
import logging
import tests.utils as utils


session_spans = [
    Span(
        datetime(2019, 4, 25, 8, 0),
        datetime(2019, 4, 25, 9, 0),
        Active()),
    Span(
        datetime(2019, 4, 25, 9, 0),
        datetime(2019, 4, 25, 10, 0),
        Inactive()),
    Span(
        datetime(2019, 4, 25, 10, 0),
        datetime(2019, 4, 25, 12, 0),
        Active()),
]


class TestServer(utils.AioHTTPTestCase):
    async def get_application(self):
        logging.disable(logging.CRITICAL)

        model = self.patch('autodesk.model.Model')
        model.get_active_time.return_value = timedelta(hours=3)
        model.get_desk_state.return_value = Down()
        model.get_session_spans.return_value = session_spans
        model.get_session_state.return_value = Active()

        timer = self.patch('autodesk.timer.Timer')
        hardware = Noop()
        operation = Operation()
        limits = (timedelta(minutes=30), timedelta(minutes=30))
        application = Application(model, timer, hardware, operation, limits)

        factory = self.patch('autodesk.application.ApplicationFactory')
        factory.create.return_value = application

        return server.setup_app(factory)

    @unittest_run_loop
    async def test_index(self):
        response = await self.client.get('/')
        self.assertEqual(200, response.status)
        expected = \
            'Currently <b>active</b> with ' + \
            'desk <b>down</b> for <b>3:00:00</b>.'
        self.assertTrue(expected in await response.text())
