class Up:
    def next(self):
        return Down()

    def test(self, _, b):
        return b

    def __eq__(self, other):
        return isinstance(other, Up)


class Down:
    def next(self):
        return Up()

    def test(self, a, _):
        return a

    def __eq__(self, other):
        return isinstance(other, Down)


class Active:
    def next(self):
        return Inactive()

    def test(self, _, b):
        return b

    def __eq__(self, other):
        return isinstance(other, Active)


class Inactive:
    def next(self):
        return Active()

    def test(self, a, _):
        return a

    def __eq__(self, other):
        return isinstance(other, Inactive)


DOWN = Down()
UP = Up()

INACTIVE = Inactive()
ACTIVE = Active()


def deserialize_session(value):
    if value in (b'inactive', 'inactive'):
        return INACTIVE
    if value in (b'active', 'active'):
        return ACTIVE

    raise ValueError('Incorrect session state "{0}".'.format(value))


def deserialize_desk(value):
    if value in (b'down', 'down'):
        return DOWN
    if value in (b'up', 'up'):
        return UP

    raise ValueError('Incorrect desk state "{0}".'.format(value))
