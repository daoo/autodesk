class NoopOutputPin:
    def __init__(self, pin):
        self.pin = pin

    def write(self, value):
        pass


class NoopPinFactory:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create(self, pin):
        return NoopOutputPin(pin)
