from autodesk.hardware.noop import NoopPinFactory


def test_factory_enter():
    with NoopPinFactory():
        pass


def test_factory_exit():
    with NoopPinFactory():
        pass


def test_factory_create():
    pin = 0
    NoopPinFactory().create(pin)


def test_pin_write_low():
    pin = 0
    NoopPinFactory().create(pin).write(0)


def test_pin_write_high():
    pin = 0
    NoopPinFactory().create(pin).write(1)
