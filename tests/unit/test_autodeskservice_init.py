import pytest
from pandas import Timedelta

from autodesk.hardware.error import HardwareError
from autodesk.states import ACTIVE, INACTIVE
from tests.autodeskservice import create_allowed_service, create_denied_service


@pytest.mark.parametrize("session_state", [ACTIVE, INACTIVE])
def test_init_schedules_when_desk_service_reports_allowed(mocker, session_state):
    (timer_mock, _, _, service) = create_allowed_service(
        mocker,
        session_state=session_state,
        limits=(Timedelta(10), Timedelta(20)),
    )

    service.init()

    timer_mock.schedule.assert_called_with(Timedelta(10), mocker.ANY)


@pytest.mark.parametrize("session_state", [ACTIVE, INACTIVE])
def test_init_denied_timer_not_scheduled(mocker, session_state):
    (timer_mock, _, _, service) = create_denied_service(
        mocker,
        session_state=session_state,
        limits=(Timedelta(10), Timedelta(20)),
    )

    service.init()

    timer_mock.schedule.assert_not_called()


def test_init_hardware_error_timer_cancelled(mocker):
    (timer_mock, session_service_stub, _, service) = create_allowed_service(mocker)
    session_service_stub.init.side_effect = HardwareError(RuntimeError())

    service.init()

    timer_mock.cancel.assert_called_once()
