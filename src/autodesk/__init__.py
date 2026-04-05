import logging
import os
from contextlib import closing
from typing import TypedDict, cast

import yaml
from aiohttp import web
from pandas import Timedelta

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


def read_yaml(path: str) -> ProgramConfig:
    with open(path) as file:
        loaded = yaml.load(file, Loader=yaml.SafeLoader)
    return cast(ProgramConfig, loaded)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    logger = logging.getLogger("program")

    config_path = os.getenv("AUTODESK_CONFIG", "config/testing.yml")
    database = os.getenv("AUTODESK_DATABASE", ":memory:")
    address = os.getenv("AUTODESK_ADDRESS", "127.0.0.1")
    port = int(os.getenv("AUTODESK_PORT", "7380"))

    logger.info('Reading config "%s"', config_path)
    config: ProgramConfig = read_yaml(config_path)

    limit_down = Timedelta(seconds=config["limits"]["down"])
    limit_up = Timedelta(seconds=config["limits"]["up"])

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
