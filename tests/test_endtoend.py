import requests
import subprocess
import unittest
import os


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        cmd = ['python3', '-u', '-m', 'autodesk.program']
        env = os.environ.copy()
        env['AUTODESK_ADDRESS'] = '127.0.0.1'
        env['AUTODESK_CONFIG'] = 'config/testing.yml'
        env['AUTODESK_DATABASE'] = ':memory:'
        env['AUTODESK_PORT'] = '8081'
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        encoding='utf-8', env=env)
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

    def test_get_index(self):
        self.assertTrue(requests.get('http://localhost:8081').ok)
