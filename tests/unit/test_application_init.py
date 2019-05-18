from autodesk.states import ACTIVE, INACTIVE, DOWN
from pandas import Timedelta
from tests.unit.application_utils import \
    make_application, TIME_ALLOWED, TIME_DENIED
import pytest


@pytest.fixture
def now_stub(mocker):
    return mocker.patch('autodesk.application.Timestamp', autospec=True).now


def test_init_inactive_light_off(mocker):
    (_, _, hardware_mock, application) = make_application(
        mocker, INACTIVE, Timedelta(0), DOWN)

    application.init()

    hardware_mock.light.assert_called_with(INACTIVE)


def test_init_active_light_on(mocker):
    (_, _, hardware_mock, application) = make_application(
        mocker, ACTIVE, Timedelta(0), DOWN)

    application.init()

    hardware_mock.light.assert_called_with(ACTIVE)


def test_init_active_denied_timer_not_scheduled(mocker, now_stub):
    now_stub.return_value = TIME_DENIED
    (_, timer_mock, _, application) = make_application(
        mocker, ACTIVE, Timedelta(0), DOWN)

    application.init()

    timer_mock.schedule.assert_not_called()


def test_init_inactive_operation_allowed_timer_not_scheduled(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, _, application) = make_application(
        mocker, INACTIVE, Timedelta(0), DOWN)

    application.init()

    timer_mock.schedule.assert_not_called()


def test_init_active_operation_allowed_timer_scheduled(mocker, now_stub):
    now_stub.return_value = TIME_ALLOWED
    (_, timer_mock, _, application) = make_application(
        mocker, ACTIVE, Timedelta(0), DOWN,
        limits=(Timedelta(10), Timedelta(20)))

    application.init()

    timer_mock.schedule.assert_called_with(Timedelta(10), mocker.ANY)
