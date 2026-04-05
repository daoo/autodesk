import asyncio

import pytest
import pytest_asyncio

import autodesk.api as api
from autodesk.application.autodeskservice import AutoDeskService
from autodesk.application.autodeskservicefactory import AutoDeskServiceFactory
from autodesk.hardware.error import HardwareError
from autodesk.hardware.noop import NoopPin
from autodesk.states import Desk, Session


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


@pytest.mark.asyncio
async def test_setup(client, service_mock):
    service_mock.init.assert_called_with()


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
