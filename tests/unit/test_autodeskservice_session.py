from datetime import timedelta

from autodesk.hardware.error import HardwareError
from autodesk.states import Desk, Session
from tests.autodeskservice import create_allowed_service, create_denied_service


def test_set_session_active_desk_down_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_allowed_service(
        mocker,
        session_state=Session.INACTIVE,
        active_time=timedelta(seconds=10),
        desk_state=Desk.DOWN,
        limits=(timedelta(seconds=20), timedelta(seconds=30)),
    )

    service.set_session(Session.ACTIVE)

    timer_mock.schedule.assert_called_with(timedelta(seconds=10), mocker.ANY)


def test_set_session_active_desk_up_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_allowed_service(
        mocker,
        session_state=Session.INACTIVE,
        active_time=timedelta(seconds=10),
        desk_state=Desk.UP,
        limits=(timedelta(seconds=20), timedelta(seconds=30)),
    )

    service.set_session(Session.ACTIVE)

    timer_mock.schedule.assert_called_with(timedelta(seconds=20), mocker.ANY)


def test_set_session_inactive_timer_cancelled(mocker):
    (timer_mock, _, _, service) = create_denied_service(
        mocker,
        session_state=Session.ACTIVE,
        desk_state=Desk.UP,
    )

    service.set_session(Session.INACTIVE)

    timer_mock.cancel.assert_called_once()


def test_set_session_timer_lambda_called_desk_service_called(mocker):
    (timer_stub, _, desk_service_mock, service) = create_allowed_service(
        mocker,
        desk_state=Desk.DOWN,
    )

    service.set_session(Session.ACTIVE)
    timer_stub.schedule.call_args[0][1]()

    desk_service_mock.set.assert_called_with(Desk.UP)


def test_set_session_timer_lambda_calls_desk_service_with_next_state(mocker):
    (timer_stub, _, desk_service_mock, service) = create_allowed_service(
        mocker,
        desk_state=Desk.UP,
    )

    service.set_session(Session.ACTIVE)
    timer_stub.schedule.call_args[0][1]()

    desk_service_mock.set.assert_called_with(Desk.DOWN)


def test_set_session_hardware_error_timer_cancelled(mocker):
    (timer_mock, session_service_stub, _, service) = create_allowed_service(
        mocker,
        session_state=Session.INACTIVE,
    )
    session_service_stub.set.side_effect = HardwareError(RuntimeError())

    service.set_session(Session.ACTIVE)

    timer_mock.cancel.assert_called_once()


def test_toggle_session_from_inactive(mocker):
    (_, session_service_mock, _, service) = create_allowed_service(
        mocker,
        session_state=Session.INACTIVE,
        active_time=timedelta(seconds=10),
        limits=(timedelta(seconds=20), timedelta(seconds=30)),
    )

    service.toggle_session()

    session_service_mock.set.assert_called_with(Session.ACTIVE)


def test_toggle_session_from_active(mocker):
    (_, session_service_mock, _, service) = create_allowed_service(
        mocker,
        session_state=Session.ACTIVE,
        active_time=timedelta(seconds=10),
        limits=(timedelta(seconds=20), timedelta(seconds=30)),
    )

    service.toggle_session()

    session_service_mock.set.assert_called_with(Session.INACTIVE)
