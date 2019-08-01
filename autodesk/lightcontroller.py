class LightController:
    def __init__(self, pin_session):
        self.pin_session = pin_session

    def set(self, state):
        value = state.test(0, 1)
        self.pin_session.write(value)
