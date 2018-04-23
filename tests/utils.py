import aiohttp.test_utils
import unittest
import unittest.mock


class TestCase(unittest.TestCase):
    def patch(self, target):
        patcher = unittest.mock.patch(target, autospec=True)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock


class AioHTTPTestCase(aiohttp.test_utils.AioHTTPTestCase):
    def patch(self, target):
        patcher = unittest.mock.patch(target, autospec=True)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock
