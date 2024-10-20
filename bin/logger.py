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


def notify(url, active):
    state = b"active" if active else b"inactive"
    requests.put(url, data=state)


def properties_handler(hostname, interface, changed, invalidated):
    print(datetime.now(), interface, changed, invalidated)
    if interface == "org.freedesktop.login1.Session":
        if "Active" in changed:
            notify(hostname, changed["Active"])


def program(hostname):
    bus = SystemBus()
    login = bus.get("org.freedesktop.login1")
    for _, _, _, _, path in login.ListSessions():
        print(f"Connecting to {path}")
        sessionbus = bus.get("org.freedesktop.login1", path)
        sessionbus.PropertiesChanged.connect(
            lambda interface, changed, invalidated: properties_handler(
                hostname, interface, changed, invalidated
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
