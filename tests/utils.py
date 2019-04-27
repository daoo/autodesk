class StubDataStore:
    def __init__(self, session_events, desk_events):
        self.session_events = session_events
        self.desk_events = desk_events

    def close(self):
        pass

    def get_session_events(self):
        return self.session_events

    def get_desk_events(self):
        return self.desk_events

    def set_session(self, date, state):
        raise RuntimeError("Not modifiable.")

    def set_desk(self, date, state):
        raise RuntimeError("Not modifiable.")

    @staticmethod
    def empty():
        return StubDataStore([], [])
