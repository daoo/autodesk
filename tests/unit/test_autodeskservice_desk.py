import pytest
from pandas import Timedelta

from autodesk.hardware.error import HardwareError
from autodesk.states import ACTIVE, DOWN, UP
from tests.autodeskservice import DESK_DENIED, TIME_ALLOWED, create_service


@pytest.mark.parametrize("session,now", DESK_DENIED)
def test_set_desk_down_denied_timer_not_scheduled(mocker, session, now):
    (timer_mock, _, _, service) = create_service(mocker, now, session, Timedelta(0), UP)

    service.set_desk(DOWN)

    timer_mock.schedule.assert_not_called()


def test_set_desk_down_allowed_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker,
        TIME_ALLOWED,
        ACTIVE,
        Timedelta(10),
        UP,
        limits=(Timedelta(20), Timedelta(30)),
    )

    service.set_desk(DOWN)

    timer_mock.schedule.assert_called_with(Timedelta(10), mocker.ANY)


def test_set_desk_up_allowed_timer_scheduled_right_time(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker,
        TIME_ALLOWED,
        ACTIVE,
        Timedelta(10),
        UP,
        limits=(Timedelta(20), Timedelta(30)),
    )

    service.set_desk(UP)

    timer_mock.schedule.assert_called_with(Timedelta(20), mocker.ANY)


@pytest.mark.parametrize("desk", [DOWN, UP])
def test_set_desk_hardware_error_timer_cancelled(mocker, desk):
    (timer_mock, _, desk_service_stub, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), desk.next()
    )
    desk_service_stub.set.side_effect = HardwareError(RuntimeError())

    service.set_desk(desk)

    timer_mock.cancel.assert_called_once()
