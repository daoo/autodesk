import logging

from autodesk.hardware.types import InputPin, OutputPin, PinFactory, PinValue


class LoggingInputPin(InputPin):
    def __init__(self, inner: InputPin):
        self.logger = logging.getLogger("hardware")
        self.inner = inner
        self.pin = inner.pin

    def read(self) -> PinValue:
        value = self.inner.read()
        self.logger.debug("read %d %d", self.pin, value)
        return value


class LoggingOutputPin(OutputPin):
    def __init__(self, inner: OutputPin):
        self.logger = logging.getLogger("hardware")
        self.inner = inner
        self.pin = inner.pin

    def write(self, value: PinValue) -> None:
        self.logger.info("write %d %d", self.pin, value)
        self.inner.write(value)


class LoggingPinFactory(PinFactory):
    def __init__(self, inner: PinFactory):
        self.logger = logging.getLogger("hardware")
        self.inner = inner

    def close(self) -> None:
        self.logger.info("close")
        self.inner.close()

    def create_input(self, pin: int) -> LoggingInputPin:
        self.logger.info("create %d", pin)
        return LoggingInputPin(self.inner.create_input(pin))

    def create_output(self, pin: int) -> LoggingOutputPin:
        self.logger.info("create %d", pin)
        return LoggingOutputPin(self.inner.create_output(pin))
