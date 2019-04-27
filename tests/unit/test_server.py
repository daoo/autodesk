from autodesk.model import Down, Up, Inactive, Active
import autodesk.server as server
import pytest


@pytest.fixture
def application(mocker):
    return mocker.patch(
        'autodesk.application.Application', autospec=True)


@pytest.fixture
async def client(mocker, application, aiohttp_client):
    factory = mocker.patch(
        'autodesk.application.ApplicationFactory', autospec=True)
    factory.create.return_value = application
    return await aiohttp_client(server.setup_app(factory))


async def test_setup(client, application):
    application.init.assert_called_with()


async def test_get_desk_down(client, application):
    application.get_desk_state.return_value = Down()
    response = await client.get('/api/desk')
    assert '0' == await response.text()


async def test_get_desk_up(client, application):
    application.get_desk_state.return_value = Up()
    response = await client.get('/api/desk')
    assert '1' == await response.text()


async def test_set_desk_down(client, application):
    response = await client.put('/api/desk', data=b'0')
    assert 200 == response.status
    application.set_desk.assert_called_with(Down())


async def test_set_desk_up(client, application):
    response = await client.put('/api/desk', data=b'1')
    assert 200 == response.status
    application.set_desk.assert_called_with(Up())


async def test_set_desk_not_allowed(client, application):
    application.set_desk.return_value = False
    response = await client.put('/api/desk', data=b'1')
    assert 403 == response.status


async def test_get_session_inactive(client, application):
    application.get_session_state.return_value = Inactive()
    response = await client.get('/api/session')
    assert '0' == await response.text()


async def test_get_session_active(client, application):
    application.get_session_state.return_value = Active()
    response = await client.get('/api/session')
    assert '1' == await response.text()


async def test_set_session_inactive(client, application):
    response = await client.put('/api/session', data=b'0')
    application.set_session.assert_called_with(Inactive())
    assert 200 == response.status


async def test_set_session_active(client, application):
    response = await client.put('/api/session', data=b'1')
    application.set_session.assert_called_with(Active())
    assert 200 == response.status
