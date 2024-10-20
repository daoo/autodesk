import pytest

from autodesk.deskcontroller import DeskController
from autodesk.states import DOWN, UP


@pytest.fixture
def sleep_fake(mocker):
    return mocker.patch("time.sleep", autospec=True)


def create_pin_fake(mocker):
    return mocker.patch("autodesk.hardware.noop.NoopPin")


def create_controller(mocker, delay):
    pin_down_fake = create_pin_fake(mocker)
    pin_up_fake = create_pin_fake(mocker)
    pin_light_fake = create_pin_fake(mocker)
    controller = DeskController(delay, pin_down_fake, pin_up_fake, pin_light_fake)
    return (pin_down_fake, pin_up_fake, pin_light_fake, controller)


@pytest.mark.parametrize("direction", [DOWN, UP])
def test_move_sleeps_for_specified_delay(mocker, sleep_fake, direction):
    sleep_mock = sleep_fake
    (_, _, _, controller) = create_controller(mocker, 1)

    controller.move(direction)

    sleep_mock.assert_called_once_with(1)


def test_move_down_correct_pin_pulled_high_and_low(mocker, sleep_fake):
    (pin_down_mock, _, _, controller) = create_controller(mocker, 1)

    controller.move(DOWN)

    pin_down_mock.write.assert_has_calls([mocker.call(1), mocker.call(0)])


def test_move_up_correct_pin_pulled_high_and_low(mocker, sleep_fake):
    (_, pin_up_mock, _, controller) = create_controller(mocker, 1)

    controller.move(UP)

    pin_up_mock.write.assert_has_calls([mocker.call(1), mocker.call(0)])


@pytest.mark.parametrize("direction", [DOWN, UP])
def test_move_light_pin_pulled_high_and_low(mocker, sleep_fake, direction):
    (_, _, pin_light_mock, controller) = create_controller(mocker, 1)

    controller.move(direction)

    pin_light_mock.write.assert_has_calls([mocker.call(1), mocker.call(0)])
