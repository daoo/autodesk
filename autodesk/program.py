from aiohttp import web
from autodesk.applicationfactory import ApplicationFactory
from autodesk.server import setup_app
from datetime import timedelta
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

logger.info('Reading config "{}"'.format(config_path))

config = None
with open(config_path, 'r') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

application_factory = ApplicationFactory(
    database,
    config['hardware'],
    (
        timedelta(seconds=config['limits']['down']),
        timedelta(seconds=config['limits']['up']),
    ),
    config['delay'],
    (
        config['motor_pins']['down'],
        config['motor_pins']['up'],
    ),
    config['light_pin'],
)

web.run_app(setup_app(application_factory), host=address, port=port)
