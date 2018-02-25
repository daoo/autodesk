import requests
import subprocess
import tempfile
import unittest

config_template = """
desk:
  delay: 1
  limits:
    down: 5
    up: 5
  motor_pins:
    down: 1
    up: 2
  light_pin: 3
server:
  database_path: ":memory:"
  address: "localhost"
  port: 8080
"""


class TestServer(unittest.TestCase):
    def setUp(self):
        config_file = tempfile.NamedTemporaryFile()
        with open(config_file.name, 'w') as file:
            file.write(config_template)
        self.addCleanup(config_file.close)

        cmd = ['python', '-u', '-m', 'autodesk.server', config_file.name]
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL,
                                        encoding='utf-8')
        while True:
            line = self.process.stdout.readline()
            if not line or 'Running on ' in line:
                break
        self.addCleanup(self.process.stdout.close)

        def stop():
            self.process.terminate()
            self.process.wait()

        self.addCleanup(stop)

    def test_server_index(self):
        self.assertTrue(requests.get('http://localhost:8080').ok)
