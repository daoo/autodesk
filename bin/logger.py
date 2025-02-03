#!/usr/bin/env python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pydbus",
#     "pygobject",
#     "requests",
# ]
# ///

import sys
from datetime import datetime

import requests
from gi.repository import GLib
from pydbus import SystemBus


def notify(url: str, active: bool):
    state = b"active" if active else b"inactive"
    requests.put(url, data=state, headers={"Content-Type": "text/plain"})


def properties_handler(url: str, interface, changed, invalidated):
    print(datetime.now(), interface, changed, invalidated)
    if interface == "org.freedesktop.login1.Session":
        if "Active" in changed:
            notify(url, changed["Active"])


def program(url: str):
    bus = SystemBus()
    login = bus.get("org.freedesktop.login1")
    for _, _, _, _, path in login.ListSessions():
        print(f"Connecting to {path}")
        sessionbus = bus.get("org.freedesktop.login1", path)
        sessionbus.PropertiesChanged.connect(
            lambda interface, changed, invalidated: properties_handler(
                url, interface, changed, invalidated
            )
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
