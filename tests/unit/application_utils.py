from autodesk.application import Application
from autodesk.operation import Operation
from autodesk.scheduler import Scheduler
from pandas import Timestamp, Timedelta


TIME_ALLOWED = Timestamp(2018, 4, 23, 13, 0)
TIME_DENIED = Timestamp(2018, 4, 23, 20, 0)


def make_application(
        mocker,
        session_state,
        active_time,
        desk_state,
        limits=(Timedelta(0), Timedelta(0))):
    model_fake = mocker.patch(
        'autodesk.model.Model', autospec=True)
    model_fake.get_active_time.return_value = active_time
    model_fake.get_session_state.return_value = session_state
    model_fake.get_desk_state.return_value = desk_state

    timer_fake = mocker.patch(
        'autodesk.timer.Timer', autospec=True)
    desk_controller_fake = mocker.patch(
        'autodesk.deskcontroller.DeskController', autospec=True)
    light_service_fake = mocker.patch(
        'autodesk.application.lightservice.LightService', autospec=True)
    application = Application(
        model_fake,
        timer_fake,
        desk_controller_fake,
        light_service_fake,
        Operation(),
        Scheduler(limits))
    return (model_fake, timer_fake, desk_controller_fake, light_service_fake,
            application)
