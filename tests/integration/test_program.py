import os
import subprocess
from urllib import error, request

import pytest


@pytest.fixture
def process():
    cmd = [
        "uv",
        "run",
        "autodesk",
        "--address=127.0.0.1",
        "--config=config/testing.toml",
        "--database=:memory:",
        "--port=7381",
    ]
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "x"
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        env=env,
    )
    assert process.stdout
    assert process.stderr

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
    try:
        with request.urlopen("http://localhost:7381") as response:
            assert 200 <= response.status < 400
    except error.HTTPError as exc:
        pytest.fail(f"GET / failed with status {exc.code}")
