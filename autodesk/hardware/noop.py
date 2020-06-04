class NoopPin:
    def __init__(self, pin):
        self.pin = pin

    def read(self):
        return 0

    def write(self, value):
        pass


class NoopPinFactory:
    def close(self):
        pass

    def create_input(self, pin):
        return NoopPin(pin)

    def create_output(self, pin):
        return NoopPin(pin)
