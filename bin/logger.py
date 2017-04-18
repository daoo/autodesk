#!/usr/bin/env python

from datetime import datetime
from gi.repository import GLib
from pydbus import SystemBus
import requests
import sys


def notify(url, active):
    state = b'1' if active else b'0'
    requests.put(url, data=state)


def properties_handler(hostname, interface, changed, invalidated):
    print(datetime.now(), interface, changed, invalidated)
    if interface == 'org.freedesktop.login1.Session':
        if 'Active' in changed:
            notify(hostname, changed['Active'])


def program(hostname):
    bus = SystemBus()
    login = bus.get('org.freedesktop.login1')
    for (sid, uid, uname, seat, path) in login.ListSessions():
        print('Connecting to {}'.format(path))
        sessionbus = bus.get('org.freedesktop.login1', path)
        sessionbus.PropertiesChanged.connect(
            lambda interface, changed, invalidated: properties_handler(
                hostname, interface, changed, invalidated))
    GLib.MainLoop().run()


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(
            'Usage: {} URL\n'.format(sys.argv[0]))
        sys.exit(1)

    try:
        program(sys.argv[1])
    except KeyboardInterrupt:
        sys.exit(0)

main()
