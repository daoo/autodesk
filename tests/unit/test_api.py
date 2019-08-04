from autodesk.states import DOWN, UP, INACTIVE, ACTIVE
import autodesk.api as api
import pytest


@pytest.fixture
def application(mocker):
    return mocker.patch(
        'autodesk.application.Application', autospec=True)


@pytest.fixture
async def client(mocker, application, aiohttp_client):
    factory = mocker.patch(
        'autodesk.applicationfactory.ApplicationFactory', autospec=True)
    factory.create.return_value = application
    return await aiohttp_client(api.setup_app(factory))


async def test_setup(client, application):
    application.init.assert_called_with()


async def test_get_desk_down(client, application):
    application.get_desk_state.return_value = DOWN
    response = await client.get('/api/desk')
    assert 'down' == await response.text()


async def test_get_desk_up(client, application):
    application.get_desk_state.return_value = UP
    response = await client.get('/api/desk')
    assert 'up' == await response.text()


async def test_set_desk_down(client, application):
    response = await client.put('/api/desk', data=b'down')
    assert 200 == response.status
    application.set_desk.assert_called_with(DOWN)


async def test_set_desk_up(client, application):
    response = await client.put('/api/desk', data=b'up')
    assert 200 == response.status
    application.set_desk.assert_called_with(UP)


async def test_set_desk_not_allowed(client, application):
    application.set_desk.return_value = False
    response = await client.put('/api/desk', data=b'up')
    assert 403 == response.status


async def test_get_session_inactive(client, application):
    application.get_session_state.return_value = INACTIVE
    response = await client.get('/api/session')
    assert 'inactive' == await response.text()


async def test_get_session_active(client, application):
    application.get_session_state.return_value = ACTIVE
    response = await client.get('/api/session')
    assert 'active' == await response.text()


async def test_set_session_inactive(client, application):
    response = await client.put('/api/session', data=b'inactive')
    application.set_session.assert_called_with(INACTIVE)
    assert 200 == response.status


async def test_set_session_active(client, application):
    response = await client.put('/api/session', data=b'active')
    application.set_session.assert_called_with(ACTIVE)
    assert 200 == response.status
