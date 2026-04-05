import asyncio
from datetime import timedelta

from autodesk.application.autodeskservice import AutoDeskService
from autodesk.application.autodeskservicefactory import AutoDeskServiceFactory
from autodesk.hardware.types import PinFactory


class DummyPinFactory(PinFactory):
    def __init__(self):
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def create_input(self, pin: int):
        return object()

    def create_output(self, pin: int):
        return object()


def test_autodeskservicefactory_create(mocker):
    factory = AutoDeskServiceFactory(
        database_path=":memory:",
        pin_factory=DummyPinFactory(),
        limits=(timedelta(minutes=20), timedelta(minutes=30)),
        delay=0.1,
        motor_pins=(2, 3),
        light_pins=(4, 5),
    )

    loop = asyncio.new_event_loop()
    service = factory.create(loop)

    assert isinstance(service, AutoDeskService)

    service.session_service.model.close()
    service.desk_service.model.close()

    loop.close()


def test_autodeskservicefactory_registers_pins(mocker):
    pin_factory_mock = mocker.create_autospec(PinFactory, instance=True)
    pin_factory_mock.create_output.return_value = mocker.Mock()
    factory = AutoDeskServiceFactory(
        database_path=":memory:",
        pin_factory=pin_factory_mock,
        limits=(timedelta(minutes=20), timedelta(minutes=30)),
        delay=0.1,
        motor_pins=(7, 8),
        light_pins=(9, 10),
    )

    loop = asyncio.new_event_loop()
    service = factory.create(loop)

    service.session_service.model.close()
    service.desk_service.model.close()

    assert pin_factory_mock.create_output.call_count == 4
    loop.close()
