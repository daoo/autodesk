import requests
import subprocess
import sys
import unittest


class TestServer(unittest.TestCase):
    def setUp(self):
        cmd = ['python', '-u', '-m', 'autodesk.server', 'sys/testing.yml']
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        encoding='utf-8')
        self.addCleanup(self.process.stdout.close)
        self.addCleanup(self.process.stderr.close)

        while True:
            line = self.process.stdout.readline()
            if not line:
                raise RuntimeError(self.process.stderr.read())
            elif 'Running on ' in line:
                break

        def stop():
            self.process.terminate()
            self.process.wait()

        self.addCleanup(stop)

    def test_server_index(self):
        self.assertTrue(requests.get('http://localhost:8081').ok)
