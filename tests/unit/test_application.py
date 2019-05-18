from autodesk.application import Application
from autodesk.hardware.noop import Noop
from autodesk.operation import Operation


def test_constructor_succeeds(mocker):
    Application(
        mocker.patch('autodesk.model.Model', autospec=True),
        mocker.patch('autodesk.timer.Timer', autospec=True),
        Noop(),
        Operation(),
        mocker.patch('autodesk.scheduler.Scheduler', autospec=True))
