import pytest
from pandas import Timestamp

from autodesk.application.sessionservice import SessionService
from autodesk.hardware.error import HardwareError
from autodesk.states import ACTIVE, INACTIVE


def create_service(mocker, session_state, now=Timestamp.min):
    model_fake = mocker.patch("autodesk.model.Model", autospec=True)
    model_fake.get_session_state.return_value = session_state

    time_service_fake = mocker.patch(
        "autodesk.application.timeservice.TimeService", autospec=True
    )
    time_service_fake.now.return_value = now

    light_controller_fake = mocker.patch(
        "autodesk.lightcontroller.LightController", autospec=True
    )
    service = SessionService(model_fake, light_controller_fake, time_service_fake)
    return (model_fake, light_controller_fake, service)


def test_init_inactive_light_off(mocker):
    (_, light_controller_mock, service) = create_service(mocker, INACTIVE)

    service.init()

    light_controller_mock.set.assert_called_with(INACTIVE)


def test_init_active_light_on(mocker):
    (_, light_controller_mock, service) = create_service(mocker, ACTIVE)

    service.init()

    light_controller_mock.set.assert_called_with(ACTIVE)


def test_set_inactive_light_off(mocker):
    (_, light_controller_mock, service) = create_service(mocker, ACTIVE)

    service.set(INACTIVE)

    light_controller_mock.set.assert_called_with(INACTIVE)


def test_set_active_light_on(mocker):
    (_, light_controller_mock, service) = create_service(mocker, INACTIVE)

    service.set(ACTIVE)

    light_controller_mock.set.assert_called_with(ACTIVE)


def test_set_active_model_set_active(mocker):
    now = Timestamp(2019, 8, 1, 13, 0)
    (model_mock, _, service) = create_service(mocker, INACTIVE, now)

    service.set(ACTIVE)

    model_mock.set_session.assert_called_with(now, ACTIVE)


def test_set_inactive_model_set_inactive(mocker):
    now = Timestamp(2019, 8, 1, 13, 0)
    (model_mock, _, service) = create_service(mocker, ACTIVE, now)

    service.set(INACTIVE)

    model_mock.set_session.assert_called_with(now, INACTIVE)


def test_set_hardware_error_is_passed_up(mocker):
    (_, light_controller_stub, service) = create_service(mocker, INACTIVE)
    light_controller_stub.set.side_effect = HardwareError(RuntimeError())

    with pytest.raises(HardwareError):
        service.set(ACTIVE)


def test_set_hardware_error_model_still_called(mocker):
    now = Timestamp(2019, 8, 1, 13, 0)
    (model_mock, light_controller_stub, service) = create_service(mocker, INACTIVE, now)
    light_controller_stub.set.side_effect = HardwareError(RuntimeError())

    try:
        service.set(ACTIVE)
    except HardwareError:
        pass

    model_mock.set_session.assert_called_with(now, ACTIVE)
