from aiohttp import web
from autodesk.controller import Controller
from autodesk.hardware import Hardware
from autodesk.model import Database, desk_from_int, session_from_int
from autodesk.timer import Timer, TimerFactory
from datetime import datetime, timedelta
import aiohttp_jinja2
import autodesk.stats as stats
import jinja2
import json
import sys
import yaml


async def route_set_session(request):
    body = await request.text()
    state = session_from_int(int(body))
    request.app['controller'].set_session(datetime.now(), state)
    return web.Response()


async def route_get_session(request):
    sessions = request.app['database'].get_session_spans(
        datetime.fromtimestamp(0), datetime.now())
    return web.Response(text=sessions[-1].data.test('0', '1'))


async def route_set_desk(request):
    body = await request.text()
    state = desk_from_int(int(body))
    ok = request.app['controller'].set_desk(datetime.now(), state)
    return web.Response(status=200 if ok else 403)


async def route_get_desk(request):
    desks = request.app['database'].get_desk_spans(
        datetime.fromtimestamp(0), datetime.now())
    return web.Response(text=desks[-1].data.test('0', '1'))


async def route_get_sessions(request):
    def format(hour, minute, value):
        return {
            'time': '{:0>2}:{:0>2}'.format(hour, minute),
            'value': str(value)
        }

    start = 7*60
    end = 19*60

    def trim_day(measurments):
        return measurments[start:end]

    def trim_week(measurments):
        return measurments[0:5]

    def decorate(measurments):
        index = 0
        for measurments in measurments:
            yield (index // 60, index % 60, measurments)
            index += 1

    daily_active_time = stats.compute_daily_active_time(
        request.app['database'].get_session_spans(
            datetime.fromtimestamp(0),
            datetime.now()
        ))
    grouped = stats.group_into_days(daily_active_time)
    decorated = [list(decorate(group)) for group in grouped]
    trimmed = trim_week([trim_day(group) for group in decorated])

    formatted = [[format(*data) for data in group] for group in trimmed]

    return web.Response(text=json.dumps(formatted), content_type='text/json')


@aiohttp_jinja2.template('index.html')
async def route_index(request):
    beginning = datetime.fromtimestamp(0)
    now = datetime.now()
    database = request.app['database']
    session_spans = database.get_session_spans(beginning, now)
    session_state = session_spans[-1].data.test('inactive', 'active')
    desk_spans = database.get_desk_spans(beginning, now)
    desk_state = desk_spans[-1].data.test('down', 'up')
    active_time = stats.compute_active_time(session_spans, desk_spans)
    return {
        'session': session_state,
        'desk': desk_state,
        'active_time': active_time
    }


def init(app):
    app['hardware'].init()
    app['timer'].update(datetime.now())


def cleanup(app):
    app['hardware'].close()
    app['database'].close()
    app['timer'].cancel()


def setup_app(hardware, database, controller, timer):
    app = web.Application()
    app['hardware'] = hardware
    app['database'] = database
    app['controller'] = controller
    app['timer'] = timer

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('srv/templates'))

    app.router.add_get('/', route_index)
    app.router.add_get('/api/session', route_get_session)
    app.router.add_put('/api/session', route_set_session)
    app.router.add_get('/api/desk', route_get_desk)
    app.router.add_put('/api/desk', route_set_desk)
    app.router.add_get('/api/sessions.json', route_get_sessions)
    app.router.add_static('/static/', 'srv/static')

    app.on_startup.append(init)
    app.on_cleanup.append(cleanup)

    return app


def main(config):
    limit_down = timedelta(seconds=config['desk']['limits']['down'])
    limit_up = timedelta(seconds=config['desk']['limits']['up'])
    limits = (limit_down, limit_up)
    motor_pins = (config['desk']['motor_pins']['down'],
                  config['desk']['motor_pins']['up'])

    hardware = Hardware(config['desk']['delay'], motor_pins,
                        config['desk']['light_pin'])
    database = Database(config['server']['database_path'])
    controller = Controller(hardware, database)

    async def action(target):
        controller.set_desk(datetime.now(), target)
    timer = Timer(limits, database, TimerFactory(action))

    controller.add_observer(timer)

    return setup_app(hardware, database, controller, timer)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: {} CONFIG.YML\n'.format(sys.argv[0]))
        sys.exit(1)

    config = None
    with open(sys.argv[1], 'r') as file:
        config = yaml.load(file)

    web.run_app(
        main(config),
        host=config['server']['address'],
        port=int(config['server']['port']))
