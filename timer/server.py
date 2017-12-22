#!/usr/bin/env python

from autodesk.desktimer import DeskTimer
from datetime import datetime, timedelta
import requests
import sys
import threading


def set_desk(server, target):
    requests.put(server + '/api/desk', data=str(target))

def update_timer(server):
    requests.get(server + '/api/timer/update')


def program(server):
    action = lambda target: set_desk(server, target)
    timer = DeskTimer(action)

    try:
        update_timer(server)
    except requests.exceptions.ConnectionError:
        # Timer service started first, let
        # webserver update us when it starts.
        pass

    try:
        while True:
            cmd = input()
            if cmd == 'cancel':
                timer.cancel()
                print('{} stopping timer'.format(datetime.now()))
            else:
                try:
                    [delay_str, target_str] = cmd.split(' ')
                    delay = timedelta(seconds=float(delay_str))
                    target = int(target_str)
                    print('{} next state is {} in {}s'.format(
                        datetime.now(), target, delay))
                    timer.schedule(delay, target)
                except ValueError:
                    sys.stderr.write('Warning: invalid data "{}"\n'.format(cmd))
    except EOFError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        timer.cancel()


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: {} SERVER\n".format(sys.argv[0]))
        sys.exit(1)
    else:
        program(sys.argv[1])

if __name__ == "__main__":
    main()
