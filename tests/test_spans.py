from autodesk.spans import Event, Span, collect, cut
import unittest


class TestSpans(unittest.TestCase):
    def test_length(self):
        self.assertEqual(Span(0, 0, None).length(), 0)
        self.assertEqual(Span(0, 1, None).length(), 1)
        self.assertEqual(Span(1, 0, None).length(), -1)

    def test_collect_empty(self):
        spans = list(collect('a', 0, 1, []))
        self.assertEqual(spans, [Span(0, 1, 'a')])

    def test_collect_inital(self):
        events = [Event(1, 'a')]
        spans = collect('b', 0, 1, events)
        initial = list(spans)[0]
        self.assertEqual(initial.data, 'b')
        self.assertEqual(initial.start, 0)

    def test_collect_final(self):
        events = [Event(1, 'a')]
        spans = collect('b', 0, 2, events)
        final = list(spans)[-1]
        self.assertEqual(final.data, 'a')
        self.assertEqual(final.end, 2)

    def test_collect_merge_initial(self):
        events = [Event(1, 'a')]
        self.assertEqual(list(collect('a', 0, 1, events)), [Span(0, 1, 'a')])

    def test_collect_merge_events(self):
        events = [Event(1, 'a'), Event(2, 'a')]
        self.assertEqual(list(collect('a', 0, 2, events)), [Span(0, 2, 'a')])

    def test_cut_empty(self):
        spans = []
        self.assertEqual(list(cut(0, 1, spans)), [])

    def test_cut_entire(self):
        spans = [Span(2, 4, 'a')]
        self.assertEqual(list(cut(2, 4, spans)), spans)

    def test_cut_part(self):
        spans = [Span(0, 3, 'a')]
        self.assertEqual(list(cut(1, 2, spans)), [Span(1, 2, 'a')])

    def test_cut_multi(self):
        spans = [Span(0, 2, 'a'), Span(2, 3, 'b'), Span(3, 5, 'a')]
        self.assertEqual(
            list(cut(1, 4, spans)),
            [Span(1, 2, 'a'), Span(2, 3, 'b'), Span(3, 4, 'a')]
        )

    def test_cut_outside(self):
        spans = [Span(2, 3, 'a')]
        self.assertEqual(list(cut(0, 1, spans)), [])
        self.assertEqual(list(cut(4, 5, spans)), [])

    def test_cut_inclusive(self):
        spans = [Span(2, 4, 'a')]
        self.assertEqual(list(cut(1, 2, spans)), [Span(2, 2, 'a')])
        self.assertEqual(list(cut(4, 5, spans)), [Span(4, 4, 'a')])

    def test_event_repr(self):
        event = Event(1, 'test')
        self.assertEqual(repr(event), 'Event(index=1, data=\'test\')')

    def test_span_repr(self):
        span = Span(1, 2, 'test')
        self.assertEqual(repr(span), 'Span(start=1, end=2, data=\'test\')')
