import os
import subprocess

import pytest
import requests


@pytest.fixture
def process():
    cmd = ["python3", "-u", "-m", "autodesk"]
    env = os.environ.copy()
    env["AUTODESK_ADDRESS"] = "127.0.0.1"
    env["AUTODESK_CONFIG"] = "config/testing.yml"
    env["AUTODESK_DATABASE"] = ":memory:"
    env["AUTODESK_PORT"] = "8081"
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", env=env
    )

    assert process.stdout is not None
    assert process.stderr is not None

    while True:
        line = process.stdout.readline()
        if not line:
            raise RuntimeError(process.stderr.read())
        elif "Running on " in line:
            break

    yield process

    process.stdout.close()
    process.stderr.close()
    process.terminate()
    process.wait()


def test_get_index(process: subprocess.Popen):
    assert process is not None
    assert requests.get("http://localhost:8081").ok
