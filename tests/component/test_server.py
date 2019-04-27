from autodesk.application import Application
from autodesk.hardware.noop import Noop
from autodesk.model import Model, Inactive, Active
from autodesk.operation import Operation
from autodesk.spans import Event
from datetime import datetime, timedelta
from tests.utils import StubDataStore
import autodesk.server as server
import pytest


SESSION_EVENTS = [
    Event(datetime(2019, 4, 25, 8, 0), Active()),
    Event(datetime(2019, 4, 25, 9, 0), Inactive()),
    Event(datetime(2019, 4, 25, 10, 0), Active()),
]


@pytest.fixture
async def client(mocker, aiohttp_client):
    datetimestub = mocker.patch(
        'autodesk.application.datetime', autospec=True)
    datetimestub.min = datetime.min
    datetimestub.now.return_value = datetime(2019, 4, 25, 12, 0)

    model = Model(StubDataStore(session_events=SESSION_EVENTS, desk_events=[]))

    timer = mocker.patch('autodesk.timer.Timer', autospec=True)
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
