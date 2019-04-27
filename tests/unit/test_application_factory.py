from autodesk.application import ApplicationFactory
from datetime import timedelta
import mock


@mock.patch('autodesk.application.Model')
@mock.patch('autodesk.application.Sqlite3DataStore')
@mock.patch('autodesk.application.Timer')
@mock.patch('autodesk.application.create_hardware')
@mock.patch('autodesk.application.Operation')
@mock.patch('autodesk.application.Application')
def test_create_constructors_called(application, operation, create_hardware,
                                    timer, sqlite3datastore, model):
    limits = (timedelta(seconds=20), timedelta(seconds=10))
    database_path = "path"
    hardware_kind = "noop"
    delay = 5
    motor_pins = (1, 2)
    light_pin = 3

    factory = ApplicationFactory(
        database_path,
        hardware_kind,
        limits,
        delay,
        motor_pins,
        light_pin)

    loop = mock.MagicMock()

    factory.create(loop)

    sqlite3datastore.assert_called_with(database_path)
    model.assert_called_with(sqlite3datastore.return_value)
    operation.assert_called_with()
    timer.assert_called_with(loop)
    create_hardware.assert_called_with(
        hardware_kind, delay, motor_pins, light_pin)
    application.assert_called_with(
        model.return_value,
        timer.return_value,
        create_hardware.return_value,
        operation.return_value,
        limits)
