from datetime import timedelta

import pytest

from autodesk.hardware.error import HardwareError
from autodesk.states import DOWN, UP
from tests.autodeskservice import (
    create_allowed_service,
    create_denied_service,
)


def test_set_desk_operation_not_allowed_does_not_schedule_timer(mocker):
    (timer_mock, _, _, service) = create_denied_service(mocker, desk_state=UP)

    allowed = service.set_desk(DOWN)

    assert allowed is False
    timer_mock.schedule.assert_not_called()


@pytest.mark.parametrize(
    ("target", "expected_delay"),
    [(DOWN, timedelta(seconds=10)), (UP, timedelta(seconds=20))],
)
def test_set_desk_allowed_timer_scheduled_right_time(mocker, target, expected_delay):
    (timer_mock, _, _, service) = create_allowed_service(
        mocker,
        active_time=timedelta(seconds=10),
        desk_state=UP,
        limits=(timedelta(seconds=20), timedelta(seconds=30)),
    )

    allowed = service.set_desk(target)

    assert allowed is True
    timer_mock.schedule.assert_called_with(expected_delay, mocker.ANY)


def test_set_desk_disallowed_by_service_returns_false(
    mocker,
):
    (timer_mock, _, desk_service_stub, service) = create_allowed_service(
        mocker,
        desk_state=UP,
    )
    desk_service_stub.set.side_effect = None
    desk_service_stub.set.return_value = False

    allowed = service.set_desk(DOWN)

    assert allowed is False
    timer_mock.schedule.assert_not_called()


@pytest.mark.parametrize("desk", [DOWN, UP])
def test_set_desk_hardware_error_timer_cancelled(mocker, desk):
    (timer_mock, _, desk_service_stub, service) = create_allowed_service(
        mocker,
        desk_state=desk.next(),
    )
    desk_service_stub.set.side_effect = HardwareError(RuntimeError())

    allowed = service.set_desk(desk)

    assert allowed is False
    timer_mock.cancel.assert_called_once()
