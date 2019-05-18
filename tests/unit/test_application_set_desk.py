from autodesk.hardware.error import HardwareError
from autodesk.states import ACTIVE, INACTIVE, DOWN, UP
from pandas import Timedelta
from tests.unit.application_utils import \
    make_application, TIME_ALLOWED, TIME_DENIED
import pytest


@pytest.fixture
def now_stub(mocker):
    return mocker.patch('autodesk.application.Timestamp', autospec=True).now


DESK_DENIED = [
    (ACTIVE, TIME_DENIED),
    (INACTIVE, TIME_ALLOWED),
    (INACTIVE, TIME_DENIED)
]


def test_set_desk_down_allowed_returns_true(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, _, application) = make_application(
        mocker, ACTIVE, Timedelta(0), DOWN)

    result = application.set_desk(DOWN)

    assert result


def test_set_desk_down_allowed_hardware_down(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, _, hardware_mock, application) = make_application(
        mocker, ACTIVE, Timedelta(0), DOWN)

    application.set_desk(DOWN)

    hardware_mock.desk.assert_called_with(DOWN)


@pytest.mark.parametrize("session,time", DESK_DENIED)
def test_set_desk_down_denied_returns_false(mocker, now_stub, session, time):
    now_stub.return_value = time
    (_, _, _, application) = make_application(
        mocker, session, Timedelta(0), UP)

    result = application.set_desk(DOWN)

    assert not result


@pytest.mark.parametrize("session,time", DESK_DENIED)
def test_set_desk_down_denied_hardware_unchanged(
        mocker, now_stub, session, time):
    now_stub.return_value = time
    (_, _, hardware_mock, application) = make_application(
        mocker, session, Timedelta(0), UP)

    application.set_desk(DOWN)

    hardware_mock.desk.assert_not_called()


@pytest.mark.parametrize("session,time", DESK_DENIED)
def test_set_desk_down_denied_timer_not_scheduled(
        mocker, now_stub, session, time):
    now_stub.return_value = time
    (_, timer_mock, _, application) = make_application(
        mocker, session, Timedelta(0), UP)

    application.set_desk(DOWN)

    timer_mock.schedule.assert_not_called()


def test_set_desk_down_allowed_timer_scheduled_right_time(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, _, application) = make_application(
        mocker, ACTIVE, Timedelta(10), UP,
        limits=(Timedelta(20), Timedelta(30)))

    application.set_desk(DOWN)

    timer_mock.schedule.assert_called_with(Timedelta(10), mocker.ANY)


def test_set_desk_up_allowed_timer_scheduled_right_time(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, _, application) = make_application(
        mocker, ACTIVE, Timedelta(10), UP,
        limits=(Timedelta(20), Timedelta(30)))

    application.set_desk(UP)

    timer_mock.schedule.assert_called_with(Timedelta(20), mocker.ANY)


@pytest.mark.parametrize("desk", [DOWN, UP])
def test_set_desk_hardware_error_timer_cancelled(mocker, now_stub, desk):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, hardware_stub, application) = make_application(
        mocker, ACTIVE, Timedelta(0), desk.next(),
        limits=(Timedelta(10), Timedelta(20)))
    hardware_stub.desk.side_effect = HardwareError(RuntimeError())

    application.set_desk(desk)

    timer_mock.cancel.assert_called_once()
