from pandas import Timedelta

from autodesk.hardware.error import HardwareError
from autodesk.states import ACTIVE, DOWN, INACTIVE, UP
from tests.autodeskservice import TIME_ALLOWED, create_service


def test_set_session_active_desk_down_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker,
        TIME_ALLOWED,
        INACTIVE,
        Timedelta(10),
        DOWN,
        limits=(Timedelta(20), Timedelta(30)),
    )

    service.set_session(ACTIVE)

    timer_mock.schedule.assert_called_with(Timedelta(10), mocker.ANY)


def test_set_session_active_desk_up_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker,
        TIME_ALLOWED,
        INACTIVE,
        Timedelta(10),
        UP,
        limits=(Timedelta(20), Timedelta(30)),
    )

    service.set_session(ACTIVE)

    timer_mock.schedule.assert_called_with(Timedelta(20), mocker.ANY)


def test_set_session_inactive_timer_cancelled(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), UP
    )

    service.set_session(INACTIVE)

    timer_mock.cancel.assert_called_once()


def test_set_session_timer_lambda_called_desk_service_called(mocker):
    (timer_stub, _, desk_service_mock, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), DOWN
    )

    service.set_session(ACTIVE)
    timer_stub.schedule.call_args[0][1]()

    desk_service_mock.set.assert_called_with(UP)


def test_set_session_timer_lambda_called_model_updated(mocker):
    (timer_stub, _, desk_service_mock, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), UP
    )

    service.set_session(ACTIVE)
    timer_stub.schedule.call_args[0][1]()

    desk_service_mock.set.assert_called_with(DOWN)


def test_set_session_hardware_error_timer_cancelled(mocker):
    (timer_mock, session_service_stub, _, service) = create_service(
        mocker, TIME_ALLOWED, INACTIVE, Timedelta(0), DOWN
    )
    session_service_stub.set.side_effect = HardwareError(RuntimeError())

    service.set_session(ACTIVE)

    timer_mock.cancel.assert_called_once()


def test_toggle_session_from_inactive(mocker):
    (_, session_service_mock, _, service) = create_service(
        mocker,
        TIME_ALLOWED,
        INACTIVE,
        Timedelta(10),
        DOWN,
        limits=(Timedelta(20), Timedelta(30)),
    )

    service.toggle_session()

    session_service_mock.set.assert_called_with(ACTIVE)


def test_toggle_session_from_active(mocker):
    (_, session_service_mock, _, service) = create_service(
        mocker,
        TIME_ALLOWED,
        ACTIVE,
        Timedelta(10),
        DOWN,
        limits=(Timedelta(20), Timedelta(30)),
    )

    service.toggle_session()

    session_service_mock.set.assert_called_with(INACTIVE)
