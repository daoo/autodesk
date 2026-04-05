from datetime import timedelta
from typing import Any

from pytest_mock import MockerFixture

from autodesk.application.autodeskservice import AutoDeskService
from autodesk.application.deskservice import DeskService
from autodesk.application.sessionservice import SessionService
from autodesk.scheduler import Scheduler
from autodesk.states import Desk, Session
from autodesk.timer import Timer

OPERATION_ALLOWED = True
OPERATION_DENIED = False
DEFAULT_SESSION_STATE = Session.ACTIVE
DEFAULT_ACTIVE_TIME = timedelta(0)
DEFAULT_DESK_STATE = Desk.DOWN
DEFAULT_LIMITS = (timedelta(0), timedelta(0))


def _create_service(
    mocker: MockerFixture,
    operation_allowed: bool,
    session_state: Session = DEFAULT_SESSION_STATE,
    active_time: timedelta = DEFAULT_ACTIVE_TIME,
    desk_state: Desk = DEFAULT_DESK_STATE,
    limits: tuple[timedelta, timedelta] = DEFAULT_LIMITS,
) -> tuple[Any, Any, Any, AutoDeskService]:
    timer_fake = mocker.create_autospec(Timer, instance=True)

    session_service_fake = mocker.create_autospec(SessionService, instance=True)
    session_service_fake.get.return_value = session_state
    session_service_fake.get_active_time.return_value = active_time

    def set_session_get_return(state):
        session_service_fake.get.return_value = state

    session_service_fake.set.side_effect = set_session_get_return

    desk_service_fake = mocker.create_autospec(DeskService, instance=True)
    desk_service_fake.get.return_value = desk_state
    desk_service_fake.operation_allowed.return_value = operation_allowed

    def set_desk_get_return(state):
        desk_service_fake.get.return_value = state
        return operation_allowed

    desk_service_fake.set.side_effect = set_desk_get_return

    service = AutoDeskService(
        Scheduler(limits),
        timer_fake,
        session_service_fake,
        desk_service_fake,
    )
    return (timer_fake, session_service_fake, desk_service_fake, service)


def create_allowed_service(
    mocker: MockerFixture,
    session_state: Session = DEFAULT_SESSION_STATE,
    active_time: timedelta = DEFAULT_ACTIVE_TIME,
    desk_state: Desk = DEFAULT_DESK_STATE,
    limits: tuple[timedelta, timedelta] = DEFAULT_LIMITS,
) -> tuple[Any, Any, Any, AutoDeskService]:
    return _create_service(
        mocker,
        OPERATION_ALLOWED,
        session_state,
        active_time,
        desk_state,
        limits,
    )


def create_denied_service(
    mocker: MockerFixture,
    session_state: Session = DEFAULT_SESSION_STATE,
    active_time: timedelta = DEFAULT_ACTIVE_TIME,
    desk_state: Desk = DEFAULT_DESK_STATE,
    limits: tuple[timedelta, timedelta] = DEFAULT_LIMITS,
) -> tuple[Any, Any, Any, AutoDeskService]:
    return _create_service(
        mocker,
        OPERATION_DENIED,
        session_state,
        active_time,
        desk_state,
        limits,
    )
