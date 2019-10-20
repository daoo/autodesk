from aiohttp import web
from autodesk.api import setup_app
from autodesk.hardware import create_pin_factory
from autodesk.application.autodeskservicefactory import AutoDeskServiceFactory
from pandas import Timedelta
import logging
import os
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)

logger = logging.getLogger('program')

config_path = os.getenv('AUTODESK_CONFIG', 'config/testing.yml')
database = os.getenv('AUTODESK_DATABASE', ':memory:')
address = os.getenv('AUTODESK_ADDRESS', '127.0.0.1')
port = int(os.getenv('AUTODESK_PORT', '8080'))

logger.info('Reading config "%s"', config_path)

config = None
with open(config_path, 'r') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

with create_pin_factory(config['hardware']) as pin_factory:
    factory = AutoDeskServiceFactory(
        database,
        pin_factory,
        (
            Timedelta(seconds=config['limits']['down']),
            Timedelta(seconds=config['limits']['up']),
        ),
        config['delay'],
        (
            config['motor_pins']['down'],
            config['motor_pins']['up'],
        ),
        (
            config['light_pins']['desk'],
            config['light_pins']['session'],
        ),
    )

    web.run_app(setup_app(factory), host=address, port=port)
