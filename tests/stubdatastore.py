import pandas as pd


class StubDataStore:
    def __init__(self, session_events, desk_events):
        self.session_events = pd.DataFrame(
            session_events, columns=["timestamp", "state"]
        )
        self.desk_events = pd.DataFrame(desk_events, columns=["timestamp", "state"])

    def close(self):
        pass

    def get_session_events(self):
        return self.session_events

    def get_desk_events(self):
        return self.desk_events

    def set_session(self, timestamp, state):
        raise RuntimeError("Not modifiable.")

    def set_desk(self, timestamp, state):
        raise RuntimeError("Not modifiable.")

    @staticmethod
    def empty():
        return StubDataStore([], [])
