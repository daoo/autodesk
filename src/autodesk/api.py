import asyncio
import logging
import traceback

import aiohttp_jinja2
import jinja2
from aiohttp import web

import autodesk.plots as plots
from autodesk.button import Button
from autodesk.hardware.error import HardwareError
from autodesk.states import Desk, Session, deserialize_desk, deserialize_session

logger = logging.getLogger("api")


async def route_set_session(request: web.Request):
    body = await request.text()
    try:
        state = deserialize_session(body)
        request.app["service"].set_session(state)
        return web.Response()
    except ValueError:
        logger.error(traceback.format_exc())
        return web.Response(text="Invalid session state", status=400)


async def route_get_session(request: web.Request):
    state = request.app["service"].get_session_state()
    assert type(state) is Session
    return web.Response(text=state.test("inactive", "active"))


async def route_set_desk(request: web.Request):
    body = await request.text()
    try:
        state = deserialize_desk(body)
        okay = request.app["service"].set_desk(state)
        return web.Response(status=200 if okay else 403)
    except ValueError:
        logger.error(traceback.format_exc())
        return web.Response(text="Invalid desk state", status=400)


async def route_get_desk(request: web.Request):
    state = request.app["service"].get_desk_state()
    assert type(state) is Desk
    return web.Response(text=state.test("down", "up"))


@aiohttp_jinja2.template("index.html")
async def route_index(request: web.Request):
    service = request.app["service"]
    session_state = service.get_session_state().test("inactive", "active")
    desk_state = service.get_desk_state().test("down", "up")
    active_time = service.get_active_time()
    counts_figure = plots.plot_weekday_hourly_count(service.compute_hourly_count())
    return {
        "session": session_state,
        "desk": desk_state,
        "active_time": active_time,
        "statistics": plots.figure_to_base64(counts_figure),
    }


async def poll_button(
    button: Button, polling_delay: float, hardware_error_delay: float
):
    while True:
        try:
            button.poll()
            await asyncio.sleep(polling_delay)
        except HardwareError as error:
            logger.debug(error)
            await asyncio.sleep(hardware_error_delay)


async def init(app: web.Application):
    loop = asyncio.get_running_loop()
    service = app["factory"].create(loop)
    service.init()
    button = Button(app["button_pin"], service)
    app["poll_button_task"] = loop.create_task(
        poll_button(button, app["button_polling_delay"], app["hardware_error_delay"])
    )
    del app["button_pin"]
    del app["factory"]
    app["service"] = service


async def cleanup(app: web.Application):
    app["poll_button_task"].cancel()


def setup_app(button_pin, factory, button_polling_delay=0.1, hardware_error_delay=5.0):
    app = web.Application()

    app["button_polling_delay"] = button_polling_delay
    app["hardware_error_delay"] = hardware_error_delay
    app["button_pin"] = button_pin
    app["factory"] = factory

    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader("autodesk", "templates"))

    app.router.add_get("/", route_index)
    app.router.add_get("/api/session", route_get_session)
    app.router.add_put("/api/session", route_set_session)
    app.router.add_get("/api/desk", route_get_desk)
    app.router.add_put("/api/desk", route_set_desk)

    app.on_startup.append(init)
    app.on_cleanup.append(cleanup)

    return app
