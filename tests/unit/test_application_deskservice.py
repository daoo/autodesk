from autodesk.application.deskservice import DeskService
from autodesk.states import DOWN, UP
import pytest


@pytest.fixture
def sleep_fake(mocker):
    return mocker.patch('time.sleep', autospec=True)


@pytest.fixture
def down_pin_fake(mocker):
    return mocker.MagicMock()


@pytest.fixture
def up_pin_fake(mocker):
    return mocker.MagicMock()


@pytest.mark.parametrize('direction', [DOWN, UP])
def test_move_sleeps_for_specified_delay(
        sleep_fake, down_pin_fake, up_pin_fake, direction):
    sleep_mock = sleep_fake
    service = DeskService(1, down_pin_fake, up_pin_fake)

    service.move(direction)

    sleep_mock.assert_called_once_with(1)


def test_move_down_correct_pin_pulled_high_and_low(
        mocker, sleep_fake, down_pin_fake, up_pin_fake):
    down_pin_mock = down_pin_fake
    service = DeskService(1, down_pin_fake, up_pin_fake)

    service.move(DOWN)

    down_pin_mock.write.assert_has_calls(
        [mocker.call(1), mocker.call(0)])


def test_move_up_correct_pin_pulled_high_and_low(
        mocker, sleep_fake, down_pin_fake, up_pin_fake):
    up_pin_mock = up_pin_fake
    service = DeskService(1, down_pin_fake, up_pin_fake)

    service.move(UP)

    up_pin_mock.write.assert_has_calls(
        [mocker.call(1), mocker.call(0)])
