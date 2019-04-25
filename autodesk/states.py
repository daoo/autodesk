class Up:
    def next(self):
        return Down()

    def test(self, a, b):
        return b

    def __eq__(self, other):
        return isinstance(other, Up)


class Down:
    def next(self):
        return Up()

    def test(self, a, b):
        return a

    def __eq__(self, other):
        return isinstance(other, Down)


class Active:
    def test(self, a, b):
        return b

    def __eq__(self, other):
        return isinstance(other, Active)


class Inactive:
    def test(self, a, b):
        return a

    def __eq__(self, other):
        return isinstance(other, Inactive)


DOWN = Down()
UP = Up()

INACTIVE = Inactive()
ACTIVE = Active()


def deserialize_session(value):
    if value == b'inactive' or value == 'inactive':
        return INACTIVE
    elif value == b'active' or value == 'active':
        return ACTIVE
    else:
        raise ValueError('Incorrect session state "{0}".'.format(value))


def deserialize_desk(value):
    if value == b'down' or value == 'down':
        return DOWN
    elif value == b'up' or value == 'up':
        return UP
    else:
        raise ValueError('Incorrect desk state "{0}".'.format(value))
