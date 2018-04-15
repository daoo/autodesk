import logging


class LoggingWrapper:
    def __init__(self, inner):
        self.logger = logging.getLogger('hardware')
        self.inner = inner

    def close(self):
        self.logger.info('close')
        self.inner.close()

    def desk(self, state):
        self.logger.info('desk %s', state.test('down', 'up'))
        self.inner.desk(state)

    def light(self, state):
        self.logger.info('light %s', state.test('off', 'on'))
        self.inner.light(state)
