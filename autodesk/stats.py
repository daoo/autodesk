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

    return buckets


def group_into_days(buckets):
    length = 24*60
    yield buckets[0*length:1*length]
    yield buckets[1*length:2*length]
    yield buckets[2*length:3*length]
    yield buckets[3*length:4*length]
    yield buckets[4*length:5*length]
    yield buckets[5*length:6*length]
    yield buckets[6*length:7*length]
