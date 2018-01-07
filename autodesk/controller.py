from autodesk.spans import Event
from datetime import time

DESK_OPERATION_ALLOWANCE_START = time(8, 0, 0)
DESK_OPERATION_ALLOWANCE_END = time(18, 0, 0)


class Operation:
    @staticmethod
    def allow(at):
        monday = 0
        friday = 4
        time_at = time(at.hour, at.minute, at.second)
        weekday = at.weekday()
        return \
            time_at >= DESK_OPERATION_ALLOWANCE_START and \
            time_at <= DESK_OPERATION_ALLOWANCE_END and \
            weekday >= monday and weekday <= friday


class Controller:
    def __init__(self, hardware, model):
        self.hardware = hardware
        self.model = model
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def set_session(self, time, state):
        self.model.insert_session_event(Event(time, state))
        self.hardware.light(state)
        for observer in self.observers:
            observer.session_changed(time, state)

    def set_desk(self, time, state):
        if not Operation.allow(time):
            for observer in self.observers:
                observer.desk_change_disallowed(time)
            return False

        self.hardware.go(state)
        self.model.insert_desk_event(Event(time, state))
        for observer in self.observers:
            observer.desk_changed(time, state)
        return True
