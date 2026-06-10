import argparse
import logging
import tomllib
from contextlib import closing
from datetime import timedelta
from typing import TypedDict, cast

from aiohttp import web

from autodesk.api import setup_app
from autodesk.application.autodeskservicefactory import AutoDeskServiceFactory
from autodesk.hardware import create_pin_factory


class LimitsConfig(TypedDict):
    down: int | float
    up: int | float


class MotorPinsConfig(TypedDict):
    down: int
    up: int


class LightPinsConfig(TypedDict):
    desk: int
    session: int


class ProgramConfig(TypedDict):
    hardware: str
    button_pin: int
    delay: float
    limits: LimitsConfig
    motor_pins: MotorPinsConfig
    light_pins: LightPinsConfig


def read_config(path: str) -> ProgramConfig:
    with open(path, "rb") as file:
        loaded = tomllib.load(file)
    return cast(ProgramConfig, loaded)


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    logger = logging.getLogger("program")

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/testing.toml")
    parser.add_argument("--database", default=":memory:")
    parser.add_argument("--address", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7380)
    args = parser.parse_args(argv)

    config_path = args.config
    database = args.database
    address = args.address
    port = args.port

    logger.info('Reading config "%s"', config_path)
    config: ProgramConfig = read_config(config_path)

    limit_down = timedelta(seconds=config["limits"]["down"])
    limit_up = timedelta(seconds=config["limits"]["up"])

    with closing(create_pin_factory(config["hardware"])) as pin_factory:
        button_pin = pin_factory.create_input(config["button_pin"])
        factory = AutoDeskServiceFactory(
            database,
            pin_factory,
            (limit_down, limit_up),
            float(config["delay"]),
            (
                config["motor_pins"]["down"],
                config["motor_pins"]["up"],
            ),
            (
                config["light_pins"]["desk"],
                config["light_pins"]["session"],
            ),
        )
        app = setup_app(button_pin, factory)
        web.run_app(app, host=address, port=port)
