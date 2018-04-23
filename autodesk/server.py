from aiohttp import web
from autodesk.model import desk_from_int, session_from_int
from datetime import datetime
import aiohttp_jinja2
import autodesk.stats as stats
import jinja2
import json


async def route_set_session(request):
    body = await request.text()
    state = session_from_int(int(body))
    request.app['application'].set_session(datetime.now(), state)
    return web.Response()


async def route_get_session(request):
    return web.Response(
        text=request.app['application'].get_session_state().test('0', '1'))


async def route_set_desk(request):
    body = await request.text()
    state = desk_from_int(int(body))
    ok = request.app['application'].set_desk(datetime.now(), state)
    return web.Response(status=200 if ok else 403)


async def route_get_desk(request):
    return web.Response(
        text=request.app['application'].get_desk_state().test('0', '1'))


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

    daily_active_time = request.app['application'].get_daily_active_time(
        datetime.min, datetime.now())
    grouped = stats.group_into_days(daily_active_time)
    decorated = [list(decorate(group)) for group in grouped]
    trimmed = trim_week([trim_day(group) for group in decorated])

    formatted = [[format(*data) for data in group] for group in trimmed]

    return web.Response(text=json.dumps(formatted), content_type='text/json')


@aiohttp_jinja2.template('index.html')
async def route_index(request):
    beginning = datetime.min
    now = datetime.now()
    application = request.app['application']
    session_state = application.get_session_state().test('inactive', 'active')
    desk_state = application.get_desk_state().test('down', 'up')
    active_time = application.get_active_time(beginning, now)
    return {
        'session': session_state,
        'desk': desk_state,
        'active_time': active_time
    }


async def init(app):
    app['application'] = app['application_factory'].create(app.loop)
    del app['application_factory']
    app['application'].init(datetime.now())


async def cleanup(app):
    app['application'].close()


def setup_app(application_factory):
    app = web.Application()
    app['application_factory'] = application_factory

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
