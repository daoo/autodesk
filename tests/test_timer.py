from autodesk.timer import Timer
from autodesk.model import Down, Up
from datetime import timedelta
import pytest
import tempfile


@pytest.fixture
def timer_path():
    with tempfile.NamedTemporaryFile() as tmp:
        yield tmp.name


def test_stop(timer_path):
    Timer(timer_path).stop()
    with open(timer_path, 'r') as fobj:
        assert fobj.read() == 'stop\n'


def test_set(timer_path):
    Timer(timer_path).set(timedelta(seconds=42), Down())
    with open(timer_path, 'r') as fobj:
        assert fobj.read() == '42 0\n'

    Timer(timer_path).set(timedelta(seconds=42), Up())
    with open(timer_path, 'r') as fobj:
        assert fobj.read() == '42 1\n'
