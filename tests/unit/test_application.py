from autodesk.application import Application
from autodesk.operation import Operation


def test_constructor_succeeds(mocker):
    Application(
        mocker.patch('autodesk.model.Model', autospec=True),
        mocker.patch('autodesk.timer.Timer', autospec=True),
        mocker.patch('autodesk.application.deskservice.DeskService',
                     autospec=True),
        mocker.patch('autodesk.application.lightservice.LightService',
                     autospec=True),
        Operation(),
        mocker.patch('autodesk.scheduler.Scheduler', autospec=True))
