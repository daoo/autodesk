from autodesk.application import Application
from autodesk.hardware.noop import Noop
from autodesk.model import Model, Down, Up, Inactive, Active
from autodesk.operation import Operation
from autodesk.spans import Event
from datetime import datetime, timedelta
from tests.utils import StubDataStore
import autodesk.server as server
import base64
import os
import pytest


SESSION_EVENTS = [
    # Tuesdays
    Event(datetime(2019, 4, 16, 14, 0), Active()),
    Event(datetime(2019, 4, 16, 18, 0), Inactive()),
    Event(datetime(2019, 4, 23, 14, 0), Active()),
    Event(datetime(2019, 4, 23, 18, 0), Inactive()),

    # Wednesdays
    Event(datetime(2019, 4, 24, 13, 0), Active()),
    Event(datetime(2019, 4, 24, 14, 0), Inactive()),

    # Thursdays
    Event(datetime(2019, 4, 25, 8, 0), Active()),
    Event(datetime(2019, 4, 25, 9, 0), Inactive()),
    Event(datetime(2019, 4, 25, 10, 0), Active()),
]

DESK_EVENTS = [
    Event(datetime(2019, 4, 25, 8, 30), Up()),
    Event(datetime(2019, 4, 25, 10, 30), Down()),
    Event(datetime(2019, 4, 25, 11, 30), Up()),
]


@pytest.fixture
async def client(mocker, aiohttp_client):
    datetimestub = mocker.patch(
        'autodesk.application.datetime', autospec=True)
    datetimestub.min = datetime.min
    datetimestub.now.return_value = datetime(2019, 4, 25, 12, 0)

    model = Model(StubDataStore(
        session_events=SESSION_EVENTS,
        desk_events=DESK_EVENTS))

    timer = mocker.patch('autodesk.timer.Timer', autospec=True)
    hardware = Noop()
    operation = Operation()
    limits = (timedelta(minutes=30), timedelta(minutes=30))
    application = Application(model, timer, hardware, operation, limits)

    factory = mocker.patch(
        'autodesk.application.ApplicationFactory', autospec=True)
    factory.create.return_value = application

    return await aiohttp_client(server.setup_app(factory))


@pytest.fixture
def testdir(request):
    return os.path.splitext(request.module.__file__)[0]


@pytest.fixture
def expected_figure(testdir):
    with open(os.path.join(testdir, 'expected_figure.png'), 'rb') as file:
        return file.read()


async def test_index(client, expected_figure):
    response = await client.get('/')
    text = await response.text()

    expected_state_string = \
        'Currently <b>active</b> with ' + \
        'desk <b>up</b> for <b>0:30:00</b>.'
    expected_figure_string = \
        base64.b64encode(expected_figure).decode('utf-8')

    assert 200 == response.status
    assert expected_state_string in text
    assert expected_figure_string in text
