import pytest

from autodesk.button import Button


@pytest.fixture
def pin_stub(mocker):
    return mocker.patch("autodesk.hardware.noop.NoopPin", autospec=True)


@pytest.fixture
def autodeskservice_mock(mocker):
    return mocker.patch(
        "autodesk.application.autodeskservice.AutoDeskService", autospec=True
    )


@pytest.fixture
def button(pin_stub, autodeskservice_mock):
    return Button(pin_stub, autodeskservice_mock)


def test_poll_read0_toggle_session_not_called(pin_stub, autodeskservice_mock, button):
    pin_stub.read.return_value = 0

    button.poll()

    autodeskservice_mock.toggle_session.assert_not_called()


def test_poll_read1_toggle_session_called(pin_stub, autodeskservice_mock, button):
    pin_stub.read.return_value = 1

    button.poll()

    autodeskservice_mock.toggle_session.assert_called_once()


def test_poll_read1_twice_toggle_session_called_only_once(
    pin_stub, autodeskservice_mock, button
):
    pin_stub.read.return_value = 1

    button.poll()
    button.poll()

    autodeskservice_mock.toggle_session.assert_called_once()
