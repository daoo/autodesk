from aiohttp import web
from autodesk.application import ApplicationFactory
from autodesk.server import setup_app
from datetime import timedelta
import logging
import sys
import yaml

if len(sys.argv) != 2:
    sys.stderr.write('Usage: {} CONFIG.YML\n'.format(sys.argv[0]))
    sys.exit(1)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)

config = None
with open(sys.argv[1], 'r') as file:
    config = yaml.load(file)

application_factory = ApplicationFactory(
    config['server']['database_path'],
    config['desk']['hardware'],
    (
        timedelta(seconds=config['desk']['limits']['down']),
        timedelta(seconds=config['desk']['limits']['up']),
    ),
    config['desk']['delay'],
    (
        config['desk']['motor_pins']['down'],
        config['desk']['motor_pins']['up'],
    ),
    config['desk']['light_pin'],
)

web.run_app(
    setup_app(application_factory),
    host=config['server']['address'],
    port=int(config['server']['port']),
)
