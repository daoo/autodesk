from autodesk.spans import Event, Span, collect, cut


def test_length():
    assert Span(0, 0, None).length() == 0
    assert Span(0, 1, None).length() == 1
    assert Span(1, 0, None).length() == -1


def test_collect_empty():
    spans = list(collect('a', 0, 1, []))
    assert spans == [Span(0, 1, 'a')]


def test_collect_inital():
    events = [Event(1, 'a')]
    spans = collect('b', 0, 1, events)
    initial = list(spans)[0]
    assert initial.data == 'b'
    assert initial.start == 0


def test_collect_final():
    events = [Event(1, 'a')]
    spans = collect('b', 0, 2, events)
    final = list(spans)[-1]
    assert final.data == 'a'
    assert final.end == 2


def test_collect_merge_initial():
    events = [Event(1, 'a')]
    assert list(collect('a', 0, 1, events)) == [Span(0, 1, 'a')]


def test_collect_merge_events():
    events = [Event(1, 'a'), Event(2, 'a')]
    assert list(collect('a', 0, 2, events)) == [Span(0, 2, 'a')]


def test_cut_empty():
    spans = []
    assert list(cut(0, 1, spans)) == []


def test_cut_entire():
    spans = [Span(2, 4, 'a')]
    assert list(cut(2, 4, spans)) == spans


def test_cut_part():
    spans = [Span(0, 3, 'a')]
    assert list(cut(1, 2, spans)) == [Span(1, 2, 'a')]


def test_cut_multi():
    spans = [Span(0, 2, 'a'), Span(2, 3, 'b'), Span(3, 5, 'a')]
    expected = [Span(1, 2, 'a'), Span(2, 3, 'b'), Span(3, 4, 'a')]
    assert list(cut(1, 4, spans)) == expected


def test_cut_outside():
    spans = [Span(2, 3, 'a')]
    assert list(cut(0, 1, spans)) == []
    assert list(cut(4, 5, spans)) == []


def test_cut_inclusive():
    spans = [Span(2, 4, 'a')]
    assert list(cut(1, 2, spans)) == [Span(2, 2, 'a')]
    assert list(cut(4, 5, spans)) == [Span(4, 4, 'a')]


def test_span_repr():
    span = Span(1, 2, 'test')
    assert repr(span) == 'Span(start=1, end=2, data=\'test\')'


def test_event_repr():
    event = Event(1, 'test')
    assert repr(event) == 'Event(index=1, data=\'test\')'
