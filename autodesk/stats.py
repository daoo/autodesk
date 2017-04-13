from datetime import time

def compute_daily_active_time(spans):
    def index(time):
        day = 60 * 24
        hour = 60
        return time.weekday() * day +  time.hour * hour + time.minute

    buckets = [0] * 7 * 24 * 60
    for span in spans:
        if span.data.active():
            for i in range(index(span.start), index(span.end)):
                buckets[i] += 1

    maximum = max(buckets)
    if maximum == 0:
        return buckets
    return [bucket / maximum for bucket in buckets]
