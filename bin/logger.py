#!/usr/bin/env python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pydbus",
#     "pygobject",
#     "requests",
# ]
# ///

import logging
import sys

import requests
from gi.repository import GLib
from pydbus import SystemBus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


def notify(url: str, active: bool):
    logging.info(f"notify {url} {active}")
    state = b"active" if active else b"inactive"
    try:
        result = requests.put(url, data=state, headers={"Content-Type": "text/plain"})
        logging.info(f"result {result}")
    except Exception as error:
        logging.error(error)


def properties_handler(url: str, interface, changed, invalidated):
    logging.info(f"handler {interface} {changed} {invalidated}")
    if interface != "org.freedesktop.login1.Session":
        return
    if "Active" in changed:
        notify(url, changed["Active"])
    elif "LockedHint" in changed:
        notify(url, not changed["LockedHint"])


def program(url: str):
    bus = SystemBus()
    login = bus.get("org.freedesktop.login1")
    for _, _, _, _, path in login.ListSessions():
        logging.info(f"connecting {path}")
        sessionbus = bus.get("org.freedesktop.login1", path)
        sessionbus.PropertiesChanged.connect(
            lambda interface, changed, invalidated: properties_handler(
                url,
                interface,
                changed,
                invalidated,
            ),
        )
    GLib.MainLoop().run()


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} URL\n")
        sys.exit(1)

    try:
        program(sys.argv[1])
    except KeyboardInterrupt:
        sys.exit(0)


main()
