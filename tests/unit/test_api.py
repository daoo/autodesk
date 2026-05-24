import asyncio
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
from autodesk.hardware.error import HardwareError
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


@pytest.fixture
def service_mock(mocker):
    return mocker.create_autospec(AutoDeskService, instance=True)


@pytest.fixture
def button_pin_stub(mocker):
    return mocker.create_autospec(NoopPin, instance=True)


@pytest_asyncio.fixture
async def client(mocker, button_pin_stub, service_mock, aiohttp_client):
    factory = mocker.create_autospec(AutoDeskServiceFactory, instance=True)
    factory.create.return_value = service_mock
    return await aiohttp_client(
        api.setup_app(
            button_pin_stub,
            factory,
            button_polling_delay=0.1,
            hardware_error_delay=0.1,
        ),
    )


@pytest_asyncio.fixture
async def index_client(mocker, aiohttp_client):
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
async def test_setup(client, service_mock):
    service_mock.init.assert_called_with()


@pytest.mark.asyncio
async def test_index(index_client, expected_figure):
    response = await index_client.get("/")
    text = await response.text()

    expected_state_string = (
        "Currently <b>active</b> with " + "desk <b>up</b> for <b>0:30:00</b>."
    )
    expected_figure_string = base64.b64encode(expected_figure).decode("utf-8")

    assert response.status == 200
    assert expected_state_string in text
    assert expected_figure_string in text


@pytest.mark.asyncio
async def test_get_desk_down(client, service_mock):
    service_mock.get_desk_state.return_value = Desk.DOWN
    response = await client.get("/api/desk")
    assert await response.text() == "down"


@pytest.mark.asyncio
async def test_get_desk_up(client, service_mock):
    service_mock.get_desk_state.return_value = Desk.UP
    response = await client.get("/api/desk")
    assert await response.text() == "up"


@pytest.mark.asyncio
async def test_set_desk_down(client, service_mock):
    response = await client.put("/api/desk", data=b"down")
    assert response.status == 200
    service_mock.set_desk.assert_called_with(Desk.DOWN)


@pytest.mark.asyncio
async def test_set_desk_up(client, service_mock):
    response = await client.put("/api/desk", data=b"up")
    assert response.status == 200
    service_mock.set_desk.assert_called_with(Desk.UP)


@pytest.mark.asyncio
async def test_set_desk_not_allowed(client, service_mock):
    service_mock.set_desk.return_value = False
    response = await client.put("/api/desk", data=b"up")
    assert response.status == 403


@pytest.mark.asyncio
async def test_set_desk_invalid(index_client):
    response = await index_client.put("/api/desk", data=b"invalid state string")
    assert response.status == 400


@pytest.mark.asyncio
async def test_get_session_inactive(client, service_mock):
    service_mock.get_session_state.return_value = Session.INACTIVE
    response = await client.get("/api/session")
    assert await response.text() == "inactive"


@pytest.mark.asyncio
async def test_get_session_active(client, service_mock):
    service_mock.get_session_state.return_value = Session.ACTIVE
    response = await client.get("/api/session")
    assert await response.text() == "active"


@pytest.mark.asyncio
async def test_set_session_inactive(client, service_mock):
    response = await client.put("/api/session", data=b"inactive")
    service_mock.set_session.assert_called_with(Session.INACTIVE)
    assert response.status == 200


@pytest.mark.asyncio
async def test_set_session_active(client, service_mock):
    response = await client.put("/api/session", data=b"active")
    service_mock.set_session.assert_called_with(Session.ACTIVE)
    assert response.status == 200


@pytest.mark.asyncio
async def test_set_session_invalid(index_client):
    response = await index_client.put("/api/session", data=b"invalid state string")
    assert response.status == 400


@pytest.mark.asyncio
async def test_button_press(client, button_pin_stub, service_mock):
    button_pin_stub.read.return_value = 1
    await asyncio.sleep(0.1)
    service_mock.toggle_session.assert_called_once()


@pytest.mark.asyncio
async def test_button_press_after_hardware_error(client, button_pin_stub, service_mock):
    button_pin_stub.read.side_effect = HardwareError("Stubbed error for unit testing.")
    await asyncio.sleep(0.1)
    button_pin_stub.read.side_effect = None
    button_pin_stub.read.return_value = 1
    await asyncio.sleep(0.1)
    service_mock.toggle_session.assert_called_once()
