from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio

from autodesk import api
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
from autodesk.sqlitedatastore import SqliteDataStore
from autodesk.timer import Timer


@pytest_asyncio.fixture
async def client(mocker, aiohttp_client):
    time_service = mocker.create_autospec(TimeService, instance=True)
    time_service.min = datetime(1970, 1, 1, tzinfo=UTC)
    time_service.now.return_value = datetime(2024, 1, 8, 12, 0, tzinfo=UTC)

    model = Model(SqliteDataStore.open(":memory:"))
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


@pytest.mark.asyncio
async def test_set_session_valid(client):
    response = await client.put("/api/session", data=b"active")
    assert response.status == 200

    response = await client.get("/")
    text = await response.text()

    assert response.status == 200
    assert "Currently <b>active</b>" in text


@pytest.mark.asyncio
async def test_set_desk_valid(client):
    response = await client.put("/api/session", data=b"active")
    assert response.status == 200

    response = await client.put("/api/desk", data=b"up")
    assert response.status == 200

    response = await client.get("/")
    text = await response.text()

    assert response.status == 200
    assert "with desk <b>up</b>" in text
