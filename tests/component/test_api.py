import base64
import os
from datetime import datetime, timedelta

import pytest
import pytest_asyncio

import autodesk.api as api
from autodesk.application.autodeskservice import AutoDeskService
from autodesk.application.autodeskservicefactory import AutoDeskServiceFactory
from autodesk.application.deskservice import DeskService
from autodesk.application.sessionservice import SessionService
from autodesk.application.timeservice import TimeService
from autodesk.deskcontroller import DeskController
from autodesk.hardware.noop import NoopPin
from autodesk.lightcontroller import LightController
from autodesk.model import Model
from autodesk.operation import Operation
from autodesk.scheduler import Scheduler
from autodesk.states import Desk, Session
from autodesk.timer import Timer
from tests.stubdatastore import fake_data_store

SESSION_EVENTS = [
    # Tuesdays
    (datetime(2019, 4, 16, 14, 0), Session.ACTIVE),
    (datetime(2019, 4, 16, 18, 0), Session.INACTIVE),
    (datetime(2019, 4, 23, 14, 0), Session.ACTIVE),
    (datetime(2019, 4, 23, 18, 0), Session.INACTIVE),
    # Wednesdays
    (datetime(2019, 4, 24, 13, 0), Session.ACTIVE),
    (datetime(2019, 4, 24, 14, 0), Session.INACTIVE),
    # Thursdays
    (datetime(2019, 4, 25, 8, 0), Session.ACTIVE),
    (datetime(2019, 4, 25, 9, 0), Session.INACTIVE),
    (datetime(2019, 4, 25, 10, 0), Session.ACTIVE),
]

DESK_EVENTS = [
    (datetime(2019, 4, 25, 8, 30), Desk.UP),
    (datetime(2019, 4, 25, 10, 30), Desk.DOWN),
    (datetime(2019, 4, 25, 11, 30), Desk.UP),
]


@pytest_asyncio.fixture
async def client(mocker, aiohttp_client):
    time_service = mocker.create_autospec(TimeService, instance=True)
    time_service.min = datetime.min
    time_service.now.return_value = datetime(2019, 4, 25, 12, 0)

    model = Model(
        fake_data_store(mocker, session_events=SESSION_EVENTS, desk_events=DESK_EVENTS),
    )

    button_pin = NoopPin(4)
    timer = mocker.create_autospec(Timer, instance=True)
    desk_controller = DeskController(0, NoopPin(0), NoopPin(1), NoopPin(3))
    light_controller = LightController(NoopPin(2))
    operation = Operation()
    limits = (timedelta(minutes=30), timedelta(minutes=30))
    scheduler = Scheduler(limits)
    session_service = SessionService(model, light_controller, time_service)
    desk_service = DeskService(operation, model, desk_controller, time_service)
    service = AutoDeskService(
        scheduler,
        timer,
        session_service,
        desk_service,
    )

    factory = mocker.create_autospec(AutoDeskServiceFactory, instance=True)
    factory.create.return_value = service

    return await aiohttp_client(api.setup_app(button_pin, factory))


@pytest.fixture
def datadir(request):
    return os.path.splitext(request.module.__file__)[0]


@pytest.fixture
def expected_figure(datadir):
    with open(os.path.join(datadir, "expected_figure.png"), "rb") as file:
        return file.read()


@pytest.mark.asyncio
async def test_index(client, expected_figure):
    response = await client.get("/")
    text = await response.text()

    expected_state_string = (
        "Currently <b>active</b> with " + "desk <b>up</b> for <b>0:30:00</b>."
    )
    expected_figure_string = base64.b64encode(expected_figure).decode("utf-8")

    assert response.status == 200
    assert expected_state_string in text
    assert expected_figure_string in text


@pytest.mark.asyncio
async def test_set_desk_invalid(client):
    response = await client.put("/api/desk", data=b"invalid state string")
    assert response.status == 400


@pytest.mark.asyncio
async def test_set_session_invalid(client):
    response = await client.put("/api/session", data=b"invalid state string")
    assert response.status == 400
