from datetime import timedelta
import numpy as np
import pandas as pd


def enumerate_hours(t1, t2):
    t = t1
    while t < t2:
        yield (t.weekday(), t.hour)
        t = t + timedelta(hours=1)


def to_dict(span):
    return {
        'start': span.start,
        'end': span.end,
        'active': span.data.active(),
    }


def compute_hourly_relative_frequency(spans):
    df = pd.DataFrame([to_dict(span) for span in spans])

    buckets = np.zeros((7, 24))
    for span in df[df.active].itertuples():
        for (day, hour) in enumerate_hours(span.start, span.end):
            buckets[day, hour] += 1

    columns = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]
    return pd.DataFrame(buckets.T, columns=columns)
