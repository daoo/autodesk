from autodesk.application import Application
from autodesk.operation import Operation


def test_constructor_succeeds(mocker):
    Application(
        mocker.patch('autodesk.model.Model', autospec=True),
        mocker.patch('autodesk.timer.Timer', autospec=True),
        mocker.patch('autodesk.deskcontroller.DeskController',
                     autospec=True),
        mocker.patch('autodesk.lightcontroller.LightController',
                     autospec=True),
        Operation(),
        mocker.patch('autodesk.scheduler.Scheduler', autospec=True))
