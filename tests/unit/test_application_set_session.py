from autodesk.hardware.error import HardwareError
from autodesk.states import ACTIVE, INACTIVE, DOWN, UP
from pandas import Timedelta
from tests.unit.application_utils import make_application, TIME_ALLOWED
import mock
import pytest


@pytest.fixture
def now_stub(mocker):
    return mocker.patch('autodesk.application.Timestamp', autospec=True).now


def test_set_session_inactive_light_off(mocker):
    (_, _, hardware_mock, application) = make_application(
        mocker, ACTIVE, Timedelta(0), DOWN)

    application.set_session(INACTIVE)

    hardware_mock.light.assert_called_with(INACTIVE)


def test_set_session_active_light_on(mocker):
    (_, _, hardware_mock, application) = make_application(
        mocker, INACTIVE, Timedelta(0), DOWN)

    application.set_session(ACTIVE)

    hardware_mock.light.assert_called_with(ACTIVE)


def test_set_session_active_model_set_active(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (model_mock, _, _, application) = make_application(
        mocker, INACTIVE, Timedelta(0), DOWN)

    application.set_session(ACTIVE)

    model_mock.set_session.assert_called_with(TIME_ALLOWED, ACTIVE)


def test_set_session_inactive_model_set_inactive(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (model_mock, _, _, application) = make_application(
        mocker, ACTIVE, Timedelta(0), DOWN)

    application.set_session(INACTIVE)

    model_mock.set_session.assert_called_with(TIME_ALLOWED, INACTIVE)


def test_set_session_active_desk_down_timer_scheduled_right_time(
        mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, _, application) = make_application(
        mocker, INACTIVE, Timedelta(10), DOWN,
        limits=(Timedelta(20), Timedelta(30)))

    application.set_session(ACTIVE)

    timer_mock.schedule.assert_called_with(Timedelta(10), mock.ANY)


def test_set_session_active_desk_up_timer_scheduled_right_time(
        mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, _, application) = make_application(
        mocker, INACTIVE, Timedelta(10), UP,
        limits=(Timedelta(20), Timedelta(30)))

    application.set_session(ACTIVE)

    timer_mock.schedule.assert_called_with(Timedelta(20), mock.ANY)


def test_set_session_inactive_timer_cancelled(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, _, application) = make_application(
        mocker, ACTIVE, Timedelta(0), UP)

    application.set_session(INACTIVE)

    timer_mock.cancel.assert_called_once()


@pytest.mark.parametrize("session", [INACTIVE, ACTIVE])
def test_set_session_hardware_error_timer_cancelled(mocker, now_stub, session):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, hardware_stub, application) = make_application(
        mocker, session, Timedelta(0), DOWN)
    hardware_stub.light.side_effect = HardwareError(RuntimeError())

    application.set_session(session)

    timer_mock.cancel.assert_called_once()


@pytest.mark.parametrize("session", [INACTIVE, ACTIVE])
def test_set_session_hardware_error_session_inactivated(
        mocker, now_stub, session):
    now_stub.return_value = TIME_ALLOWED
    (model_mock, _, hardware_stub, application) = make_application(
        mocker, session, Timedelta(0), DOWN)
    hardware_stub.light.side_effect = HardwareError(RuntimeError())

    application.set_session(session)

    model_mock.set_session.assert_called_with(TIME_ALLOWED, INACTIVE)


def test_set_session_timer_lambda_called_hardware_called(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_stub, hardware_mock, application) = make_application(
        mocker, ACTIVE, Timedelta(0), DOWN)

    application.set_session(ACTIVE)
    timer_stub.schedule.call_args[0][1]()

    hardware_mock.desk.assert_called_with(UP)


def test_set_session_timer_lambda_called_model_updated(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (model_mock, timer_stub, _, application) = make_application(
        mocker, ACTIVE, Timedelta(0), UP)

    application.set_session(ACTIVE)
    timer_stub.schedule.call_args[0][1]()

    model_mock.set_desk.assert_called_with(TIME_ALLOWED, DOWN)
