from pandas import Timedelta, Timestamp

from autodesk.application.autodeskservice import AutoDeskService
from autodesk.operation import Operation
from autodesk.scheduler import Scheduler
from autodesk.states import ACTIVE, INACTIVE

TIME_ALLOWED = Timestamp(2018, 4, 23, 13, 0)
TIME_DENIED = Timestamp(2018, 4, 23, 21, 0)
DESK_DENIED = [(ACTIVE, TIME_DENIED), (INACTIVE, TIME_ALLOWED), (INACTIVE, TIME_DENIED)]


def create_service(
    mocker,
    now,
    session_state,
    active_time,
    desk_state,
    limits=(Timedelta(0), Timedelta(0)),
):
    timer_fake = mocker.patch("autodesk.timer.Timer", autospec=True)

    time_service_fake = mocker.patch(
        "autodesk.application.timeservice.TimeService", autospec=True
    )
    time_service_fake.now.return_value = now

    session_service_fake = mocker.patch(
        "autodesk.application.sessionservice.SessionService", autospec=True
    )
    session_service_fake.get.return_value = session_state
    session_service_fake.get_active_time.return_value = active_time

    def set_session_get_return(state):
        session_service_fake.get.return_value = state

    session_service_fake.set.side_effect = set_session_get_return

    desk_service_fake = mocker.patch(
        "autodesk.application.deskservice.DeskService", autospec=True
    )
    desk_service_fake.get.return_value = desk_state

    def set_desk_get_return(state):
        desk_service_fake.get.return_value = state

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
