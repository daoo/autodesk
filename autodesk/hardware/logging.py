import logging


class LoggingOutputPin:
    def __init__(self, inner):
        self.logger = logging.getLogger('hardware')
        self.inner = inner

    def write(self, value):
        self.logger.info('write %d %d', self.inner.pin, value)
        self.inner.write(value)


class LoggingOutputPinFactory:
    def __init__(self, inner):
        self.logger = logging.getLogger('hardware')
        self.inner = inner

    def __enter__(self):
        self.inner.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info('close')
        self.inner.__exit__(exc_type, exc_val, exc_tb)

    def create(self, pin):
        self.logger.info('create %d', pin)
        return LoggingOutputPin(self.inner.create(pin))
