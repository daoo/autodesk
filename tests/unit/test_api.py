from autodesk.states import DOWN, UP, INACTIVE, ACTIVE
import asyncio
import autodesk.api as api
import pytest


@pytest.fixture
def service_mock(mocker):
    return mocker.patch(
        'autodesk.application.autodeskservice.AutoDeskService', autospec=True)


@pytest.fixture
def button_pin_fake(mocker):
    return mocker.patch('autodesk.hardware.noop.NoopPin')


@pytest.fixture
async def client(mocker, button_pin_fake, service_mock, aiohttp_client):
    factory = mocker.patch(
        'autodesk.application.autodeskservicefactory.AutoDeskServiceFactory',
        autospec=True)
    factory.create.return_value = service_mock
    return await aiohttp_client(
        api.setup_app(button_pin_fake, factory))


async def test_setup(client, service_mock):
    service_mock.init.assert_called_with()


async def test_get_desk_down(client, service_mock):
    service_mock.get_desk_state.return_value = DOWN
    response = await client.get('/api/desk')
    assert 'down' == await response.text()


async def test_get_desk_up(client, service_mock):
    service_mock.get_desk_state.return_value = UP
    response = await client.get('/api/desk')
    assert 'up' == await response.text()


async def test_set_desk_down(client, service_mock):
    response = await client.put('/api/desk', data=b'down')
    assert 200 == response.status
    service_mock.set_desk.assert_called_with(DOWN)


async def test_set_desk_up(client, service_mock):
    response = await client.put('/api/desk', data=b'up')
    assert 200 == response.status
    service_mock.set_desk.assert_called_with(UP)


async def test_set_desk_not_allowed(client, service_mock):
    service_mock.set_desk.return_value = False
    response = await client.put('/api/desk', data=b'up')
    assert 403 == response.status


async def test_get_session_inactive(client, service_mock):
    service_mock.get_session_state.return_value = INACTIVE
    response = await client.get('/api/session')
    assert 'inactive' == await response.text()


async def test_get_session_active(client, service_mock):
    service_mock.get_session_state.return_value = ACTIVE
    response = await client.get('/api/session')
    assert 'active' == await response.text()


async def test_set_session_inactive(client, service_mock):
    response = await client.put('/api/session', data=b'inactive')
    service_mock.set_session.assert_called_with(INACTIVE)
    assert 200 == response.status


async def test_set_session_active(client, service_mock):
    response = await client.put('/api/session', data=b'active')
    service_mock.set_session.assert_called_with(ACTIVE)
    assert 200 == response.status


async def test_button_press(client, button_pin_fake, service_mock):
    button_pin_fake.read.return_value = 1
    await asyncio.sleep(0.2)
    service_mock.toggle_session.assert_called_once()
