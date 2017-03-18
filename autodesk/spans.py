class Event:
    def __init__(self, index, data):
        self.index = index
        self.data = data

    def __eq__(self, other):
        return self.index == other.index and self.data == other.data

    def __repr__(self):
        return 'Event(index={}, data={})'.format(
            repr(self.index), repr(self.data))


class Span:
    def __init__(self, start, end, data):
        self.start = start
        self.end = end
        self.data = data

    def length(self):
        return self.end - self.start

    def __eq__(self, other):
        return \
                self.start == other.start and \
                self.end == other.end and \
                self.data == other.data

    def __repr__(self):
        return 'Span(start={}, end={}, data={})'.format(
            repr(self.start), repr(self.end), repr(self.data))


def collect(default_data, initial, final, events):
    start = initial
    data = default_data
    for event in events:
        assert start <= event.index
        if data == event.data:
            continue
        yield Span(start, event.index, data)
        start = event.index
        data = event.data
    yield Span(start, final, data)


def cut(start, end, spans):
    for span in spans:
        if span.end < start or span.start > end:
            continue

        a = start if span.start < start else span.start
        b = end if span.end > end else span.end
        yield Span(a, b, span.data)


def count(spans, data, start=0):
    return sum((span.length() for span in spans if span.data == data), start)
