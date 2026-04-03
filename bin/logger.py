#!/usr/bin/env python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pydbus",
#     "pygobject",
# ]
# ///

import logging
import sys
from urllib import error as urlerror
from urllib import request as urlrequest

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
        req = urlrequest.Request(
            url,
            data=state,
            headers={"Content-Type": "text/plain"},
            method="PUT",
        )
        with urlrequest.urlopen(req) as response:
            logging.info(f"result status={response.status}")
    except urlerror.HTTPError as http_error:
        logging.error(
            "http error status=%s reason=%s",
            http_error.code,
            http_error.reason,
        )
    except Exception as exc:
        logging.error(exc)


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
