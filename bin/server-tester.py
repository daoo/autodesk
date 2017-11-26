#!/usr/bin/env python

from nanomsg import Socket, PUSH
import msgpack
import sys


def interpolate(str):
    try:
        return int(str)
    except ValueError:
        return str


with Socket(PUSH) as socket:
    socket.connect(b'tcp://127.0.0.1:12345')
    socket.send(msgpack.packb([interpolate(arg) for arg in sys.argv[1:]]))
