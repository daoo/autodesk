from aiohttp import web
from autodesk.server import setup_app
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

web.run_app(
    setup_app(config),
    host=config['server']['address'],
    port=int(config['server']['port']))
