import logging


class LoggingPin:
    def __init__(self, inner):
        self.logger = logging.getLogger("hardware")
        self.inner = inner

    def read(self):
        value = self.inner.read()
        self.logger.debug("read %d %d", self.inner.pin, value)
        return value

    def write(self, value):
        self.logger.info("write %d %d", self.inner.pin, value)
        self.inner.write(value)


class LoggingPinFactory:
    def __init__(self, inner):
        self.logger = logging.getLogger("hardware")
        self.inner = inner

    def close(self):
        self.logger.info("close")
        self.inner.close()

    def create_input(self, pin):
        self.logger.info("create %d", pin)
        return LoggingPin(self.inner.create_input(pin))

    def create_output(self, pin):
        self.logger.info("create %d", pin)
        return LoggingPin(self.inner.create_output(pin))
