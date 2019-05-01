from autodesk.application import Application
from autodesk.hardware.noop import Noop
from autodesk.model import Model
from autodesk.operation import Operation
from autodesk.states import DOWN, UP, INACTIVE, ACTIVE
from pandas import Timestamp, Timedelta
from tests.utils import StubDataStore
import autodesk.server as server
import base64
import os
import pytest


SESSION_EVENTS = [
    # Tuesdays
    (Timestamp(2019, 4, 16, 14, 0), ACTIVE),
    (Timestamp(2019, 4, 16, 18, 0), INACTIVE),
    (Timestamp(2019, 4, 23, 14, 0), ACTIVE),
    (Timestamp(2019, 4, 23, 18, 0), INACTIVE),

    # Wednesdays
    (Timestamp(2019, 4, 24, 13, 0), ACTIVE),
    (Timestamp(2019, 4, 24, 14, 0), INACTIVE),

    # Thursdays
    (Timestamp(2019, 4, 25, 8, 0), ACTIVE),
    (Timestamp(2019, 4, 25, 9, 0), INACTIVE),
    (Timestamp(2019, 4, 25, 10, 0), ACTIVE),
]

DESK_EVENTS = [
    (Timestamp(2019, 4, 25, 8, 30), UP),
    (Timestamp(2019, 4, 25, 10, 30), DOWN),
    (Timestamp(2019, 4, 25, 11, 30), UP),
]


@pytest.fixture
async def client(mocker, aiohttp_client):
    timestamp = mocker.patch(
        'autodesk.application.Timestamp', autospec=True)
    timestamp.min = Timestamp.min
    timestamp.now.return_value = Timestamp(2019, 4, 25, 12, 0)

    model = Model(StubDataStore(
        session_events=SESSION_EVENTS,
        desk_events=DESK_EVENTS))

    timer = mocker.patch(
        'autodesk.timer.Timer', autospec=True)
    hardware = Noop()
    operation = Operation()
    limits = (Timedelta(minutes=30), Timedelta(minutes=30))
    application = Application(model, timer, hardware, operation, limits)

    factory = mocker.patch(
        'autodesk.applicationfactory.ApplicationFactory', autospec=True)
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
        'desk <b>up</b> for <b>0 days 00:30:00</b>.'
    expected_figure_string = \
        base64.b64encode(expected_figure).decode('utf-8')

    assert 200 == response.status
    assert expected_state_string in text
    assert expected_figure_string in text


async def test_set_desk_invalid(client):
    response = await client.put('/api/desk', data=b'invalid state string')
    assert 400 == response.status


async def test_set_session_invalid(client):
    response = await client.put('/api/session', data=b'invalid state string')
    assert 400 == response.status
