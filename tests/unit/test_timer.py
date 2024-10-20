import pytest
from pandas import Timedelta

from autodesk.timer import Timer


@pytest.fixture
def loop(mocker):
    return mocker.patch("asyncio.AbstractEventLoop", autospec=True)


@pytest.fixture
def callback(mocker):
    return mocker.Mock()


@pytest.fixture
def timer(loop):
    return Timer(loop)


def test_schedule_call_later_called(loop, callback, timer):
    timer.schedule(Timedelta(seconds=10), callback)
    loop.call_later.assert_called_with(10.0, callback)


def test_schedule_with_previous_its_cancelled(mocker, loop, callback, timer):
    loop.call_later.return_value = timer1 = mocker.Mock()
    timer.schedule(Timedelta(seconds=10), callback)
    loop.call_later.return_value = timer2 = mocker.Mock()
    timer.schedule(Timedelta(seconds=10), callback)
    timer1.cancel.assert_called_once()
    timer2.cancel.assert_not_called()


def test_cancel_cancels(mocker, loop, callback, timer):
    call_later = mocker.Mock()
    loop.call_later.return_value = call_later
    timer.schedule(Timedelta(seconds=10), callback)
    timer.cancel()
    call_later.cancel.assert_called_once()


def test_not_running_cancel_nothing_happens(mocker, loop, timer):
    call_later = mocker.Mock()
    loop.call_later.return_value = call_later
    timer.cancel()
    call_later.cancel.assert_not_called()
