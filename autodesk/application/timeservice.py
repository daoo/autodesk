from pandas import Timestamp


class TimeService:
    def __init__(self):
        self.__min = Timestamp.min

    @property
    def min(self):
        return self.__min

    def now(self):
        return Timestamp.now()
