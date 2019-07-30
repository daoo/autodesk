from autodesk.application.autodeskservice import AutoDeskService
from autodesk.hardware.error import HardwareError
from autodesk.operation import Operation
from autodesk.scheduler import Scheduler
from autodesk.states import INACTIVE, ACTIVE, DOWN, UP
from pandas import Timestamp, Timedelta
import pytest


TIME_ALLOWED = Timestamp(2018, 4, 23, 13, 0)
TIME_DENIED = Timestamp(2018, 4, 23, 20, 0)
DESK_DENIED = [
    (ACTIVE, TIME_DENIED),
    (INACTIVE, TIME_ALLOWED),
    (INACTIVE, TIME_DENIED)
]


def create_service(
        mocker,
        now,
        session_state,
        active_time,
        desk_state,
        limits=(Timedelta(0), Timedelta(0))):
    timer_fake = mocker.patch(
        'autodesk.timer.Timer', autospec=True)

    time_service_fake = mocker.patch(
        'autodesk.application.timeservice.TimeService', autospec=True)
    time_service_fake.now.return_value = now

    session_service_fake = mocker.patch(
        'autodesk.application.sessionservice.SessionService', autospec=True)
    session_service_fake.get.return_value = session_state
    session_service_fake.get_active_time.return_value = active_time
    def set_session_get_return(state):
        session_service_fake.get.return_value = state
    session_service_fake.set.side_effect = set_session_get_return

    desk_service_fake = mocker.patch(
        'autodesk.application.deskservice.DeskService', autospec=True)
    desk_service_fake.get.return_value = desk_state
    def set_desk_get_return(state):
        desk_service_fake.get.return_value = state
    desk_service_fake.set.side_effect = set_desk_get_return

    service = AutoDeskService(
        Operation(),
        Scheduler(limits),
        timer_fake,
        time_service_fake,
        session_service_fake,
        desk_service_fake)
    return (timer_fake, session_service_fake, desk_service_fake, service)


def test_init_active_denied_timer_not_scheduled(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_DENIED, ACTIVE, Timedelta(0), DOWN)

    service.init()

    timer_mock.schedule.assert_not_called()


def test_init_inactive_operation_allowed_timer_not_scheduled(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_ALLOWED, INACTIVE, Timedelta(0), DOWN)

    service.init()

    timer_mock.schedule.assert_not_called()


def test_init_active_operation_allowed_timer_scheduled(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), DOWN,
        limits=(Timedelta(10), Timedelta(20)))

    service.init()

    timer_mock.schedule.assert_called_with(Timedelta(10), mocker.ANY)


def test_init_hardware_error_timer_cancelled(mocker):
    (timer_mock, session_service_stub, _, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), DOWN)
    session_service_stub.init.side_effect = HardwareError(RuntimeError())

    service.init()

    timer_mock.cancel.assert_called_once()


@pytest.mark.parametrize("session,now", DESK_DENIED)
def test_set_desk_down_denied_timer_not_scheduled(
        mocker, session, now):
    (timer_mock, _, _, service) = create_service(
        mocker, now, session, Timedelta(0), UP)

    service.set_desk(DOWN)

    timer_mock.schedule.assert_not_called()


def test_set_desk_down_allowed_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(10), UP,
        limits=(Timedelta(20), Timedelta(30)))

    service.set_desk(DOWN)

    timer_mock.schedule.assert_called_with(Timedelta(10), mocker.ANY)


def test_set_desk_up_allowed_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(10), UP,
        limits=(Timedelta(20), Timedelta(30)))

    service.set_desk(UP)

    timer_mock.schedule.assert_called_with(Timedelta(20), mocker.ANY)


@pytest.mark.parametrize("desk", [DOWN, UP])
def test_set_desk_hardware_error_timer_cancelled(mocker, desk):
    (timer_mock, _, desk_service_stub, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), desk.next())
    desk_service_stub.set.side_effect = HardwareError(RuntimeError())

    service.set_desk(desk)

    timer_mock.cancel.assert_called_once()


def test_set_session_active_desk_down_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_ALLOWED, INACTIVE, Timedelta(10), DOWN,
        limits=(Timedelta(20), Timedelta(30)))

    service.set_session(ACTIVE)

    timer_mock.schedule.assert_called_with(Timedelta(10), mocker.ANY)


def test_set_session_active_desk_up_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_ALLOWED, INACTIVE, Timedelta(10), UP,
        limits=(Timedelta(20), Timedelta(30)))

    service.set_session(ACTIVE)

    timer_mock.schedule.assert_called_with(Timedelta(20), mocker.ANY)


def test_set_session_inactive_timer_cancelled(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), UP)

    service.set_session(INACTIVE)

    timer_mock.cancel.assert_called_once()


def test_set_session_timer_lambda_called_desk_service_called(mocker):
    (timer_stub, _, desk_service_mock, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), DOWN)

    service.set_session(ACTIVE)
    timer_stub.schedule.call_args[0][1]()

    desk_service_mock.set.assert_called_with(UP)


def test_set_session_timer_lambda_called_model_updated(mocker):
    (timer_stub, _, desk_service_mock, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), UP)

    service.set_session(ACTIVE)
    timer_stub.schedule.call_args[0][1]()

    desk_service_mock.set.assert_called_with(DOWN)


def test_set_session_hardware_error_timer_cancelled(mocker):
    (timer_mock, session_service_stub, _, service) = create_service(
        mocker, TIME_ALLOWED, INACTIVE, Timedelta(0), DOWN)
    session_service_stub.set.side_effect = HardwareError(RuntimeError())

    service.set_session(ACTIVE)

    timer_mock.cancel.assert_called_once()
