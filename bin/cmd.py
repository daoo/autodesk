#!/usr/bin/env python

import hardware
import sys


def main(direction, timeDelta):
    pin = None
    if direction == "up":
        pin = hardware.pinUp
    elif direction == "down":
        pin = hardware.pinDown
    else:
        sys.exit(1)

    try:
        hardware.setup()
        hardware.go(pin, timeDelta)
    finally:
        hardware.cleanup()


if len(sys.argv) != 3:
    sys.stderr.write("Usage: {} up/down seconds\n".format(sys.argv[0]))
    sys.exit(1)

main(sys.argv[1], float(sys.argv[2]))
