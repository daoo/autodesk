class Stats:
    def __init__(self, database):
        self.database = database

    def compute_daily_active_time(self, initial, final):
        def index(time):
            day = 60 * 24
            hour = 60
            return time.weekday() * day +  time.hour * hour + time.minute

        spans = self.database.get_session_spans(initial=initial, final=final)

        buckets = [0] * 7 * 24 * 60
        for span in spans:
            if span.data.active():
                for i in range(index(span.start), index(span.end)):
                    buckets[i] += 1

        maximum = max(buckets)
        if maximum == 0:
            return buckets
        return [bucket / maximum for bucket in buckets]
