import logging

from autodesk.hardware.types import InputPin, OutputPin, PinFactory, PinValue


class TracingInputPin(InputPin):
    def __init__(self, inner: InputPin):
        self.logger = logging.getLogger("hardware")
        self.inner = inner
        self.pin = inner.pin

    def read(self) -> PinValue:
        value = self.inner.read()
        self.logger.debug("read %d %d", self.pin, value)
        return value


class TracingOutputPin(OutputPin):
    def __init__(self, inner: OutputPin):
        self.logger = logging.getLogger("hardware")
        self.inner = inner
        self.pin = inner.pin

    def write(self, value: PinValue) -> None:
        self.logger.info("write %d %d", self.pin, value)
        self.inner.write(value)


class TracingPinFactory(PinFactory):
    def __init__(self, inner: PinFactory):
        self.logger = logging.getLogger("hardware")
        self.inner = inner

    def close(self) -> None:
        self.logger.info("close")
        self.inner.close()

    def create_input(self, pin: int) -> TracingInputPin:
        self.logger.info("create %d", pin)
        return TracingInputPin(self.inner.create_input(pin))

    def create_output(self, pin: int) -> TracingOutputPin:
        self.logger.info("create %d", pin)
        return TracingOutputPin(self.inner.create_output(pin))
