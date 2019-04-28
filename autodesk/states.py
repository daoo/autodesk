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
