import pytest
from pandas import Timedelta, Timestamp

from autodesk.application.deskservice import DeskService
from autodesk.hardware.error import HardwareError
from autodesk.operation import Operation
from autodesk.states import ACTIVE, DOWN, INACTIVE, UP

TIME_ALLOWED = Timestamp(2018, 4, 23, 13, 0)
TIME_DENIED = Timestamp(2018, 4, 23, 21, 0)
DESK_DENIED = [(ACTIVE, TIME_DENIED), (INACTIVE, TIME_ALLOWED), (INACTIVE, TIME_DENIED)]


def create_service(mocker, now, session_state, active_time, desk_state):
    model_fake = mocker.patch("autodesk.model.Model", autospec=True)
    model_fake.get_active_time.return_value = active_time
    model_fake.get_session_state.return_value = session_state
    model_fake.get_desk_state.return_value = desk_state

    time_service_fake = mocker.patch(
        "autodesk.application.timeservice.TimeService", autospec=True
    )
    time_service_fake.now.return_value = now

    desk_controller_fake = mocker.patch(
        "autodesk.deskcontroller.DeskController", autospec=True
    )
    service = DeskService(
        Operation(), model_fake, desk_controller_fake, time_service_fake
    )
    return (model_fake, desk_controller_fake, service)


@pytest.mark.parametrize("session,now", DESK_DENIED)
def test_set_denied_desk_controller_not_called(mocker, session, now):
    (_, desk_controller_mock, service) = create_service(
        mocker, now, session, Timedelta(0), DOWN
    )

    service.set(UP)

    desk_controller_mock.move.assert_not_called()


@pytest.mark.parametrize("session,now", DESK_DENIED)
def test_set_denied_desk_model_not_updated(mocker, session, now):
    (model_mock, _, service) = create_service(mocker, now, session, Timedelta(0), DOWN)

    service.set(UP)

    model_mock.set_desk.assert_not_called()


@pytest.mark.parametrize("direction", [DOWN, UP])
def test_set_allowed_model_updated(mocker, direction):
    (model_mock, _, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), DOWN
    )

    service.set(direction)

    model_mock.set_desk.assert_called_with(TIME_ALLOWED, direction)


def test_set_allowed_desk_controller_called(mocker):
    (_, desk_controller_mock, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), DOWN
    )

    service.set(DOWN)

    desk_controller_mock.move.assert_called_with(DOWN)


def test_set_hardware_error_is_passed_up(mocker):
    (model_mock, desk_controller_stub, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), DOWN
    )
    desk_controller_stub.move.side_effect = HardwareError(RuntimeError())

    with pytest.raises(HardwareError):
        service.set(UP)


def test_set_hardware_error_model_not_updated(mocker):
    (model_mock, desk_controller_stub, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), DOWN
    )
    desk_controller_stub.move.side_effect = HardwareError(RuntimeError())

    try:
        service.set(UP)
    except HardwareError:
        pass

    model_mock.set_desk.assert_not_called()
