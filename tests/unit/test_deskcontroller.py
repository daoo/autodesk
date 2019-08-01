from autodesk.deskcontroller import DeskController
from autodesk.states import DOWN, UP
import pytest


@pytest.fixture
def sleep_fake(mocker):
    return mocker.patch('time.sleep', autospec=True)


def create_controller(mocker, delay):
    pin_down_fake = mocker.MagicMock()
    pin_up_fake = mocker.MagicMock()
    controller = DeskController(delay, pin_down_fake, pin_up_fake)
    return (pin_down_fake, pin_up_fake, controller)


@pytest.mark.parametrize('direction', [DOWN, UP])
def test_move_sleeps_for_specified_delay(mocker, sleep_fake, direction):
    sleep_mock = sleep_fake
    (_, _, controller) = create_controller(mocker, 1)

    controller.move(direction)

    sleep_mock.assert_called_once_with(1)


def test_move_down_correct_pin_pulled_high_and_low(mocker, sleep_fake):
    (pin_down_mock, _, controller) = create_controller(mocker, 1)

    controller.move(DOWN)

    pin_down_mock.write.assert_has_calls(
        [mocker.call(1), mocker.call(0)])


def test_move_up_correct_pin_pulled_high_and_low(mocker, sleep_fake):
    (_, pin_up_mock, controller) = create_controller(mocker, 1)

    controller.move(UP)

    pin_up_mock.write.assert_has_calls(
        [mocker.call(1), mocker.call(0)])
