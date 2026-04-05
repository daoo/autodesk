from pandas import Timedelta, Timestamp

from autodesk.application.autodeskservice import AutoDeskService
from autodesk.application.deskservice import DeskService
from autodesk.application.sessionservice import SessionService
from autodesk.application.timeservice import TimeService
from autodesk.operation import Operation
from autodesk.scheduler import Scheduler
from autodesk.states import ACTIVE, INACTIVE
from autodesk.timer import Timer

TIME_ALLOWED = Timestamp(2018, 4, 23, 13, 0)
TIME_DENIED = Timestamp(2018, 4, 23, 21, 0)
DESK_DENIED = [(ACTIVE, TIME_DENIED), (INACTIVE, TIME_ALLOWED), (INACTIVE, TIME_DENIED)]
DEFAULT_LIMITS = (Timedelta(0), Timedelta(0))


def create_service(
    mocker,
    now,
    session_state,
    active_time,
    desk_state,
    limits=DEFAULT_LIMITS,
):
    timer_fake = mocker.create_autospec(Timer, instance=True)

    time_service_fake = mocker.create_autospec(TimeService, instance=True)
    time_service_fake.now.return_value = now

    session_service_fake = mocker.create_autospec(SessionService, instance=True)
    session_service_fake.get.return_value = session_state
    session_service_fake.get_active_time.return_value = active_time

    def set_session_get_return(state):
        session_service_fake.get.return_value = state

    session_service_fake.set.side_effect = set_session_get_return

    desk_service_fake = mocker.create_autospec(DeskService, instance=True)
    desk_service_fake.get.return_value = desk_state

    def set_desk_get_return(state):
        desk_service_fake.get.return_value = state
        return True

    desk_service_fake.set.side_effect = set_desk_get_return

    service = AutoDeskService(
        Operation(),
        Scheduler(limits),
        timer_fake,
        time_service_fake,
        session_service_fake,
        desk_service_fake,
    )
    return (timer_fake, session_service_fake, desk_service_fake, service)
