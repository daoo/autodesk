from autodesk.states import INACTIVE, DOWN
from pandas import Timedelta
from tests.unit.application_utils import make_application


def test_close_timer_cancelled(mocker):
    (_, timer_mock, _, application) = make_application(
        mocker, INACTIVE, Timedelta(0), DOWN)

    application.close()

    timer_mock.cancel.assert_called_once()


def test_close_hardware_closed(mocker):
    (_, _, hardware_mock, application) = make_application(
        mocker, INACTIVE, Timedelta(0), DOWN)

    application.close()

    hardware_mock.close.assert_called_once()


def test_close_model_closed(mocker):
    (model_mock, _, _, application) = make_application(
        mocker, INACTIVE, Timedelta(0), DOWN)

    application.close()

    model_mock.close.assert_called_once()
