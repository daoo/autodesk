from pandas import Timedelta

from autodesk.hardware.error import HardwareError
from autodesk.states import ACTIVE, DOWN, INACTIVE
from tests.autodeskservice import TIME_ALLOWED, TIME_DENIED, create_service


def test_init_active_denied_timer_not_scheduled(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_DENIED, ACTIVE, Timedelta(0), DOWN
    )

    service.init()

    timer_mock.schedule.assert_not_called()


def test_init_inactive_operation_allowed_timer_not_scheduled(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker, TIME_ALLOWED, INACTIVE, Timedelta(0), DOWN
    )

    service.init()

    timer_mock.schedule.assert_not_called()


def test_init_active_operation_allowed_timer_scheduled(mocker):
    (timer_mock, _, _, service) = create_service(
        mocker,
        TIME_ALLOWED,
        ACTIVE,
        Timedelta(0),
        DOWN,
        limits=(Timedelta(10), Timedelta(20)),
    )

    service.init()

    timer_mock.schedule.assert_called_with(Timedelta(10), mocker.ANY)


def test_init_hardware_error_timer_cancelled(mocker):
    (timer_mock, session_service_stub, _, service) = create_service(
        mocker, TIME_ALLOWED, ACTIVE, Timedelta(0), DOWN
    )
    session_service_stub.init.side_effect = HardwareError(RuntimeError())

    service.init()

    timer_mock.cancel.assert_called_once()
