from autodesk.application import Application
from autodesk.hardware.noop import Noop
from autodesk.model import Down, Inactive, Active
from autodesk.operation import Operation
from autodesk.spans import Span
from datetime import datetime, timedelta
import autodesk.server as server
import pytest


SESSION_SPANS = [
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


@pytest.fixture
async def client(mocker, aiohttp_client):
    model = mocker.patch(
        'autodesk.model.Model', autospec=True)
    model.get_active_time.return_value = timedelta(hours=3)
    model.get_desk_state.return_value = Down()
    model.get_session_spans.return_value = SESSION_SPANS
    model.get_session_state.return_value = Active()

    timer = mocker.patch(
        'autodesk.timer.Timer', autospec=True)
    hardware = Noop()
    operation = Operation()
    limits = (timedelta(minutes=30), timedelta(minutes=30))
    application = Application(model, timer, hardware, operation, limits)

    factory = mocker.patch(
        'autodesk.application.ApplicationFactory', autospec=True)
    factory.create.return_value = application

    return await aiohttp_client(server.setup_app(factory))


async def test_index(client):
    response = await client.get('/')
    assert 200 == response.status
    expected = \
        'Currently <b>active</b> with ' + \
        'desk <b>down</b> for <b>3:00:00</b>.'
    assert expected in await response.text()
