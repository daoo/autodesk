import contextlib
from datetime import datetime

import pytest

from autodesk.application.sessionservice import SessionService
from autodesk.application.timeservice import TimeService
from autodesk.hardware.error import HardwareError
from autodesk.lightcontroller import LightController
from autodesk.model import Model
from autodesk.states import Session


def create_service(mocker, session_state, now=datetime.min):
    model_fake = mocker.create_autospec(Model, instance=True)
    model_fake.get_session_state.return_value = session_state

    time_service_fake = mocker.create_autospec(TimeService, instance=True)
    time_service_fake.now.return_value = now

    light_controller_fake = mocker.create_autospec(LightController, instance=True)
    service = SessionService(model_fake, light_controller_fake, time_service_fake)
    return (model_fake, light_controller_fake, service)


def test_init_inactive_light_off(mocker):
    (_, light_controller_mock, service) = create_service(mocker, Session.INACTIVE)

    service.init()

    light_controller_mock.set.assert_called_with(Session.INACTIVE)


def test_init_active_light_on(mocker):
    (_, light_controller_mock, service) = create_service(mocker, Session.ACTIVE)

    service.init()

    light_controller_mock.set.assert_called_with(Session.ACTIVE)


def test_set_inactive_light_off(mocker):
    (_, light_controller_mock, service) = create_service(mocker, Session.ACTIVE)

    service.set(Session.INACTIVE)

    light_controller_mock.set.assert_called_with(Session.INACTIVE)


def test_set_active_light_on(mocker):
    (_, light_controller_mock, service) = create_service(mocker, Session.INACTIVE)

    service.set(Session.ACTIVE)

    light_controller_mock.set.assert_called_with(Session.ACTIVE)


def test_set_active_model_set_active(mocker):
    now = datetime(2019, 8, 1, 13, 0)
    (model_mock, _, service) = create_service(mocker, Session.INACTIVE, now)

    service.set(Session.ACTIVE)

    model_mock.set_session.assert_called_with(now, Session.ACTIVE)


def test_set_inactive_model_set_inactive(mocker):
    now = datetime(2019, 8, 1, 13, 0)
    (model_mock, _, service) = create_service(mocker, Session.ACTIVE, now)

    service.set(Session.INACTIVE)

    model_mock.set_session.assert_called_with(now, Session.INACTIVE)


def test_set_hardware_error_is_passed_up(mocker):
    (_, light_controller_stub, service) = create_service(mocker, Session.INACTIVE)
    light_controller_stub.set.side_effect = HardwareError(RuntimeError())

    with pytest.raises(HardwareError):
        service.set(Session.ACTIVE)


def test_set_hardware_error_model_still_called(mocker):
    now = datetime(2019, 8, 1, 13, 0)
    (model_mock, light_controller_stub, service) = create_service(
        mocker, Session.INACTIVE, now
    )
    light_controller_stub.set.side_effect = HardwareError(RuntimeError())

    with contextlib.suppress(HardwareError):
        service.set(Session.ACTIVE)

    model_mock.set_session.assert_called_with(now, Session.ACTIVE)
