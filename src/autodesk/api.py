import asyncio
import logging
from typing import Any, cast

import aiohttp_jinja2
import jinja2
from aiohttp import web

import autodesk.plots as plots
from autodesk.application.autodeskservice import AutoDeskService
from autodesk.application.autodeskservicefactory import AutoDeskServiceFactory
from autodesk.button import Button
from autodesk.hardware.error import HardwareError
from autodesk.hardware.types import InputPin
from autodesk.states import Desk, Session, deserialize_desk, deserialize_session

logger = logging.getLogger("api")


def _service(app: web.Application) -> AutoDeskService:
    return cast(AutoDeskService, app["service"])


async def route_set_session(request: web.Request) -> web.Response:
    body = await request.text()
    try:
        state = deserialize_session(body)
        _service(request.app).set_session(state)
        return web.Response()
    except ValueError:
        logger.exception("invalid session state body")
        return web.Response(text="Invalid session state", status=400)


async def route_get_session(request: web.Request) -> web.Response:
    state = _service(request.app).get_session_state()
    assert type(state) is Session
    return web.Response(text=state.label())


async def route_set_desk(request: web.Request) -> web.Response:
    body = await request.text()
    try:
        state = deserialize_desk(body)
        okay = _service(request.app).set_desk(state)
        return web.Response(status=200 if okay else 403)
    except ValueError:
        logger.exception("invalid desk state body")
        return web.Response(text="Invalid desk state", status=400)


async def route_get_desk(request: web.Request) -> web.Response:
    state = _service(request.app).get_desk_state()
    assert type(state) is Desk
    return web.Response(text=state.label())


@aiohttp_jinja2.template("index.html")
async def route_index(request: web.Request) -> dict[str, Any]:
    service = _service(request.app)
    session_state = service.get_session_state().label()
    desk_state = service.get_desk_state().label()
    active_time = service.get_active_time()
    return {
        "session": session_state,
        "desk": desk_state,
        "active_time": active_time,
        "statistics": plots.plot_weekday_hourly_count_base64(
            service.compute_hourly_count(),
        ),
    }


async def poll_button(
    button: Button,
    polling_delay: float,
    hardware_error_delay: float,
) -> None:
    while True:
        try:
            button.poll()
            await asyncio.sleep(polling_delay)
        except HardwareError as error:
            logger.debug(error)
            await asyncio.sleep(hardware_error_delay)


async def init(app: web.Application) -> None:
    loop = asyncio.get_running_loop()
    factory = cast(AutoDeskServiceFactory, app["factory"])
    service = factory.create(loop)
    service.init()
    button_pin = cast(InputPin, app["button_pin"])
    button = Button(button_pin, service)
    app["poll_button_task"] = loop.create_task(
        poll_button(button, app["button_polling_delay"], app["hardware_error_delay"]),
    )
    del app["button_pin"]
    del app["factory"]
    app["service"] = service


async def cleanup(app: web.Application) -> None:
    cast(asyncio.Task[None], app["poll_button_task"]).cancel()


def setup_app(
    button_pin: InputPin,
    factory: AutoDeskServiceFactory,
    button_polling_delay: float = 0.1,
    hardware_error_delay: float = 5.0,
) -> web.Application:
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
