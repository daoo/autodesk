from autodesk.hardware.noop import NoopPinFactory


def test_factory_close():
    factory = NoopPinFactory()

    factory.close()


def test_factory_create_input():
    pin = 0
    NoopPinFactory().create_input(pin)


def test_factory_create_output():
    pin = 0
    NoopPinFactory().create_output(pin)


def test_pin_read():
    pin = 0
    value = NoopPinFactory().create_input(pin).read()
    assert value == 0


def test_pin_write_high():
    pin = 0
    NoopPinFactory().create_output(pin).write(1)


def test_pin_write_low():
    pin = 0
    NoopPinFactory().create_output(pin).write(0)
