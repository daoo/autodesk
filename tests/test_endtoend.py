import requests
import subprocess
import unittest


class TestProgram(unittest.TestCase):
    def test_incorrect_command_line_arguments(self):
        cmd = ['python3', '-u', '-m', 'autodesk.program']
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        encoding='utf-8')
        self.addCleanup(self.process.stdout.close)
        self.addCleanup(self.process.stderr.close)

        self.process.wait()

        self.assertTrue(self.process.stderr.readline())
        self.assertEquals(self.process.returncode, 1)


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        cmd = ['python3', '-u', '-m', 'autodesk.program', 'config/testing.yml']
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

    def test_get_index(self):
        self.assertTrue(requests.get('http://localhost:8081').ok)
