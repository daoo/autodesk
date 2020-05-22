from aiohttp import web
from autodesk.button import Button
from autodesk.states import deserialize_session, deserialize_desk
import aiohttp_jinja2
import asyncio
import autodesk.plots as plots
import jinja2


async def route_set_session(request):
    body = await request.text()
    try:
        state = deserialize_session(body)
        request.app['service'].set_session(state)
        return web.Response()
    except ValueError as error:
        return web.Response(text=str(error), status=400)


async def route_get_session(request):
    state = request.app['service'].get_session_state()
    return web.Response(text=state.test('inactive', 'active'))


async def route_set_desk(request):
    body = await request.text()
    try:
        state = deserialize_desk(body)
        okay = request.app['service'].set_desk(state)
        return web.Response(status=200 if okay else 403)
    except ValueError as error:
        return web.Response(text=str(error), status=400)


async def route_get_desk(request):
    state = request.app['service'].get_desk_state()
    return web.Response(text=state.test('down', 'up'))


@aiohttp_jinja2.template('index.html')
async def route_index(request):
    service = request.app['service']
    session_state = service.get_session_state().test('inactive', 'active')
    desk_state = service.get_desk_state().test('down', 'up')
    active_time = service.get_active_time()
    counts_figure = plots.plot_weekday_hourly_count(
        service.compute_hourly_count())
    return {
        'session': session_state,
        'desk': desk_state,
        'active_time': active_time,
        'statistics': plots.figure_to_base64(counts_figure)
    }


async def init(app):
    loop = asyncio.get_running_loop()
    button_pin = app['button_pin']
    service = app['factory'].create(loop)
    service.init()
    button = Button(button_pin, service)
    loop.create_task(button.poll())
    del app['button_pin']
    del app['factory']
    app['service'] = service


async def cleanup(app):
    pass


def setup_app(button_pin, factory):
    app = web.Application()
    app['button_pin'] = button_pin
    app['factory'] = factory

    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('autodesk', 'templates'))

    app.router.add_get('/', route_index)
    app.router.add_get('/api/session', route_get_session)
    app.router.add_put('/api/session', route_set_session)
    app.router.add_get('/api/desk', route_get_desk)
    app.router.add_put('/api/desk', route_set_desk)

    app.on_startup.append(init)
    app.on_cleanup.append(cleanup)

    return app
