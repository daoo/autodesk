import requests
import subprocess
import unittest


class TestServer(unittest.TestCase):
    def setUp(self):
        cmd = ['python', '-u', '-m', 'autodesk.server', 'sys/testing.yml']
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
