class NoopPin:
    def __init__(self, pin):
        self.pin = pin

    def read(self):
        return 0

    def write(self, value):
        pass


class NoopPinFactory:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_input(self, pin):
        return NoopPin(pin)

    def create_output(self, pin):
        return NoopPin(pin)
