from datetime import datetime


def get_minute(time):
    return time.hour * 60 + time.minute


class Stats:
    def __init__(self, database):
        self.database = database

    def compute_daily_active_time(self, initial, final):
        spans = self.database.get_session_spans(initial=initial, final=final)

        buckets = [0] * 24*60
        for span in spans:
            if span.data.active():
                for i in range(get_minute(span.start), get_minute(span.end)):
                    buckets[i] += 1

        maximum = max(buckets)
        if maximum == 0:
            return buckets
        return [bucket / maximum for bucket in buckets]
