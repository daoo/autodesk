from autodesk.application import Application
from autodesk.hardware.error import HardwareError
from autodesk.model import Active, Inactive, Down, Up
from autodesk.operation import Operation
from autodesk.spans import Event
from datetime import datetime, timedelta
import mock
import pytest

time_allowed = datetime(2018, 4, 23, 13, 0)
time_denied = datetime(2018, 4, 23, 20, 0)
limits = (timedelta(seconds=20), timedelta(seconds=10))


@pytest.fixture
def now(mocker):
    return mocker.patch('autodesk.application.datetime', autospec=True).now


@pytest.fixture
def model(mocker):
    return mocker.patch('autodesk.model.Model', autospec=True)


@pytest.fixture
def timer(mocker):
    return mocker.patch('autodesk.timer.Timer', autospec=True)


@pytest.fixture
def hardware(mocker):
    return mocker.patch('autodesk.hardware.noop.Noop', autospec=True)


@pytest.fixture
def application(model, timer, hardware):
    return Application(model, timer, hardware, Operation(), limits)


def test_init_inactive_light_off(model, application, hardware):
    model.get_session_state.return_value = Inactive()

    application.init()

    hardware.light.assert_called_with(Inactive())


def test_init_active_light_on(model, application, hardware):
    model.get_session_state.return_value = Active()
    model.get_active_time.return_value = timedelta(0)
    model.get_desk_state.return_value = Down()

    application.init()

    hardware.light.assert_called_with(Active())


def test_init_active_denied_timer_not_scheduled(model, timer, application,
                                                now):
    now.return_value = time_denied
    model.get_session_state.return_value = Active()

    application.init()

    timer.cancel.assert_not_called()
    timer.schedule.assert_not_called()


def test_init_inactive_operation_allowed_timer_not_scheduled(model,
                                                             timer,
                                                             application):
    model.get_active_time.return_value = timedelta(seconds=10)
    model.get_session_state.return_value = Inactive()

    application.init()

    timer.schedule.assert_not_called()
    timer.cancel.assert_not_called()


def test_init_active_operation_allowed_timer_scheduled(model, timer,
                                                       application, now):
    model.get_active_time.return_value = timedelta(seconds=10)
    model.get_desk_state.return_value = Down()
    model.get_session_state.return_value = Active()
    now.return_value = time_allowed

    application.init()

    timer.schedule.assert_called_with(timedelta(seconds=10), mock.ANY)
    timer.cancel.assert_not_called()


def test_close_timer_cancelled(timer, application):
    application.close()

    timer.cancel.assert_called_once()


def test_close_hardware_closed(hardware, application):
    application.close()

    hardware.close.assert_called_once()


def test_close_model_closed(model, application):
    application.close()

    model.close.assert_called_once()


def test_set_session_inactive_light_off(hardware, application):
    application.set_session(Inactive())

    hardware.light.assert_called_with(Inactive())


def test_set_session_active_light_on(model, hardware, application):
    model.get_desk_state.return_value = Down()
    model.get_active_time.return_value = timedelta(0)
    application.set_session(Active())

    hardware.light.assert_called_with(Active())


def test_set_session_inactive_model_set_inactive(model, application, now):
    now.return_value = time_allowed

    application.set_session(Inactive())

    model.set_session.assert_called_with(Event(time_allowed, Inactive()))


def test_set_session_active_timer_scheduled(model, application, now):
    model.get_desk_state.return_value = Down()
    model.get_active_time.return_value = timedelta(0)
    now.return_value = time_allowed

    application.set_session(Active())

    model.set_session.assert_called_with(Event(time_allowed, Active()))


def test_set_session_inactive_timer_cancelled(timer, application):
    application.set_session(Inactive())

    timer.schedule.assert_not_called()
    timer.cancel.assert_called_once()


@pytest.mark.parametrize("session", [Down(), Up()])
def test_set_session_hardware_error(model, timer, hardware, application, now,
                                    session):
    now.return_value = time_allowed
    hardware.light.side_effect = HardwareError(RuntimeError())

    application.set_session(session)

    timer.schedule.assert_not_called()
    timer.cancel.assert_called_once()
    model.set_session.assert_called_with(Event(time_allowed, Inactive()))


def test_set_desk_down_allowed_hardware_down(model, now, application,
                                             hardware):
    model.get_active_time.return_value = timedelta(0)
    model.get_session_state.return_value = Active()
    now.return_value = time_allowed

    application.set_desk(Down())

    hardware.desk.assert_called_with(Down())


desk_denied = [
    (Active(), time_denied),
    (Inactive(), time_allowed),
    (Inactive(), time_denied)
]


@pytest.mark.parametrize("session,time", desk_denied)
def test_set_desk_down_denied_hardware_unchanged(model, hardware, application,
                                                 now, session, time):
    model.get_session_state.return_value = session
    now.return_value = time

    application.set_desk(Down())

    hardware.desk.assert_not_called()


@pytest.mark.parametrize("session,time", desk_denied)
def test_set_desk_down_denied_timer_not_scheduled(model, timer, application,
                                                  now, session, time):
    now.return_value = time
    model.get_session_state.return_value = session

    application.set_desk(Down())

    timer.cancel.assert_not_called()
    timer.schedule.assert_not_called()


@pytest.mark.parametrize("desk,seconds", [(Down(), 20), (Up(), 10)])
def test_set_desk_allowed_timer_scheduled(model, timer, application, now, desk,
                                          seconds):
    model.get_active_time.return_value = timedelta(0)
    model.get_session_state.return_value = Active()
    now.return_value = time_allowed

    application.set_desk(desk)

    timer.schedule.assert_called_with(timedelta(seconds=seconds), mock.ANY)


@pytest.mark.parametrize("desk", [Down(), Up()])
def test_set_desk_hardware_error(model, timer, hardware, application, now,
                                 desk):
    model.get_session_state.return_value = Active()
    now.return_value = time_allowed
    hardware.desk.side_effect = HardwareError(RuntimeError())

    application.set_desk(desk)

    timer.schedule.assert_not_called()
    timer.cancel.assert_called_once()
    model.set_desk.assert_not_called()


def test_set_session_timer_lambda_called_desk_down(model, timer, hardware,
                                                   application, now):
    model.get_active_time.return_value = timedelta(0)
    model.get_session_state.return_value = Active()
    model.get_desk_state.return_value = Down()
    now.return_value = time_allowed

    application.set_session(Active())
    timer.schedule.call_args[0][1]()

    hardware.desk.assert_called_with(Up())
