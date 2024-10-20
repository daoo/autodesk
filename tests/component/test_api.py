import base64
import os

import pytest
from pandas import Timedelta, Timestamp

import autodesk.api as api
from autodesk.application.autodeskservice import AutoDeskService
from autodesk.application.deskservice import DeskService
from autodesk.application.sessionservice import SessionService
from autodesk.deskcontroller import DeskController
from autodesk.hardware.noop import NoopPin
from autodesk.lightcontroller import LightController
from autodesk.model import Model
from autodesk.operation import Operation
from autodesk.scheduler import Scheduler
from autodesk.states import ACTIVE, DOWN, INACTIVE, UP
from tests.stubdatastore import fake_data_store

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
def client(mocker, event_loop, aiohttp_client):
    time_service = mocker.patch(
        "autodesk.application.timeservice.TimeService", autospec=True
    )
    time_service.min = Timestamp.min
    time_service.now.return_value = Timestamp(2019, 4, 25, 12, 0)

    model = Model(
        fake_data_store(mocker, session_events=SESSION_EVENTS, desk_events=DESK_EVENTS)
    )

    button_pin = NoopPin(4)
    timer = mocker.patch("autodesk.timer.Timer", autospec=True)
    desk_controller = DeskController(0, NoopPin(0), NoopPin(1), NoopPin(3))
    light_controller = LightController(NoopPin(2))
    operation = Operation()
    limits = (Timedelta(minutes=30), Timedelta(minutes=30))
    scheduler = Scheduler(limits)
    session_service = SessionService(model, light_controller, time_service)
    desk_service = DeskService(operation, model, desk_controller, time_service)
    service = AutoDeskService(
        operation, scheduler, timer, time_service, session_service, desk_service
    )

    factory = mocker.patch(
        "autodesk.application.autodeskservicefactory.AutoDeskServiceFactory",
        autospec=True,
    )
    factory.create.return_value = service

    return event_loop.run_until_complete(
        aiohttp_client(api.setup_app(button_pin, factory))
    )


@pytest.fixture
def testdir(request):
    return os.path.splitext(request.module.__file__)[0]


@pytest.fixture
def expected_figure(testdir):
    with open(os.path.join(testdir, "expected_figure.png"), "rb") as file:
        return file.read()


@pytest.mark.asyncio
async def test_index(client, expected_figure):
    response = await client.get("/")
    text = await response.text()

    expected_state_string = (
        "Currently <b>active</b> with " + "desk <b>up</b> for <b>0 days 00:30:00</b>."
    )
    expected_figure_string = base64.b64encode(expected_figure).decode("utf-8")

    assert 200 == response.status
    assert expected_state_string in text
    assert expected_figure_string in text


@pytest.mark.asyncio
async def test_set_desk_invalid(client):
    response = await client.put("/api/desk", data=b"invalid state string")
    assert 400 == response.status


@pytest.mark.asyncio
async def test_set_session_invalid(client):
    response = await client.put("/api/session", data=b"invalid state string")
    assert 400 == response.status
