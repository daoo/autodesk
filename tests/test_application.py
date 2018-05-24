from autodesk.application import Application
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
def operation(mocker):
    return mocker.patch('autodesk.operation.Operation', autospec=True)


@pytest.fixture
def application(model, timer, hardware):
    return Application(model, timer, hardware, Operation(), limits)


def test_init_inactive_light_off(model, application, hardware):
    model.get_session_state.return_value = Inactive()

    application.init()

    hardware.light.assert_called_with(Inactive())


def test_init_active_light_on(model, application, hardware):
    model.get_session_state.return_value = Active()

    application.init()

    hardware.light.assert_called_with(Active())


def test_init_active_operation_denied_timer_not_scheduled(model, application,
                                                          timer):
    model.get_session_state.return_value = Active()

    application.init()

    timer.cancel.assert_not_called()
    timer.schedule.assert_not_called()


def test_init_inactive_operation_allowed_timer_not_scheduled(model,
                                                             application,
                                                             timer):
    model.get_active_time.return_value = timedelta(seconds=10)
    model.get_session_state.return_value = Inactive()

    application.init()

    timer.schedule.assert_not_called()
    timer.cancel.assert_not_called()


def test_init_active_operation_allowed_timer_scheduled(model, now, application,
                                                       timer):
    model.get_active_time.return_value = timedelta(seconds=10)
    model.get_desk_state.return_value = Down()
    model.get_session_state.return_value = Active()
    now.return_value = time_allowed

    application.init()

    timer.schedule.assert_called_with(timedelta(seconds=10), mock.ANY)
    timer.cancel.assert_not_called()


def test_close_timer_cancelled(application, timer):
    application.close()

    timer.cancel.assert_called_once()


def test_close_hardware_closed(application, hardware):
    application.close()

    hardware.close.assert_called_once()


def test_close_model_closed(application, model):
    application.close()

    model.close.assert_called_once()


def test_get_active_time_returns_from_model(application, model):
    ret = application.get_active_time()

    assert ret == model.get_active_time.return_value


def test_get_session_state_returns_from_model(application, model):
    ret = application.get_session_state()

    assert ret == model.get_session_state.return_value


def test_get_desk_state_returns_from_model(application, model):
    ret = application.get_desk_state()

    assert ret == model.get_desk_state.return_value


@mock.patch('autodesk.application.stats', autospec=True)
def test_get_daily_active_time_calls_stats_with_session_spans(stats,
                                                              application,
                                                              model):
    ret = application.get_daily_active_time()

    stats.compute_daily_active_time.assert_called_with(
        model.get_session_spans.return_value)
    assert ret == stats.compute_daily_active_time.return_value


def test_set_session_inactive_light_off(application, hardware):
    application.set_session(Inactive())

    hardware.light.assert_called_with(Inactive())


def test_set_session_active_light_on(model, application, hardware):
    model.get_desk_state.return_value = Down()
    model.get_active_time.return_value = timedelta(0)
    application.set_session(Active())

    hardware.light.assert_called_with(Active())


def test_set_session_inactive_model_set_inactive(now, application, model):
    now.return_value = time_allowed

    application.set_session(Inactive())

    model.set_session.assert_called_with(Event(time_allowed, Inactive()))


def test_set_session_active_timer_scheduled(model, now, application):
    model.get_desk_state.return_value = Down()
    model.get_active_time.return_value = timedelta(0)
    now.return_value = time_allowed

    application.set_session(Active())

    model.set_session.assert_called_with(Event(time_allowed, Active()))


def test_set_session_inactive_timer_cancelled(application, timer):
    application.set_session(Inactive())

    timer.schedule.assert_not_called()
    timer.cancel.assert_called_once()


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
def test_set_desk_down_denied_hardware_unchanged(model, now, application,
                                                 hardware, session, time):
    model.get_session_state.return_value = session
    now.return_value = time

    application.set_desk(Down())

    hardware.desk.assert_not_called()


@pytest.mark.parametrize("desk,seconds", [(Down(), 20), (Up(), 10)])
def test_set_desk_allowed_timer_scheduled(model, now, application, timer, desk,
                                          seconds):
    model.get_active_time.return_value = timedelta(0)
    model.get_session_state.return_value = Active()
    now.return_value = time_allowed

    application.set_desk(desk)

    timer.schedule.assert_called_with(timedelta(seconds=seconds), mock.ANY)


def test_set_desk_down_operation_denied_timer_not_scheduled(application,
                                                            timer):
    application.set_desk(Down())

    timer.cancel.assert_not_called()
    timer.schedule.assert_not_called()


def test_set_desk_down_inactive_timer_not_scheduled(application, timer):
    application.set_desk(Down())

    timer.cancel.assert_not_called()
    timer.schedule.assert_not_called()


def test_set_session_timer_lambda_called_desk_down(model, now, application,
                                                   timer, hardware):
    model.get_active_time.return_value = timedelta(0)
    model.get_session_state.return_value = Active()
    model.get_desk_state.return_value = Down()
    now.return_value = time_allowed

    application.set_session(Active())
    timer.schedule.call_args[0][1]()

    hardware.desk.assert_called_with(Up())
