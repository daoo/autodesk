#!/usr/bin/env python

from datetime import datetime, timedelta
import requests
import sys
import threading


def go(server, target):
    requests.put(server + '/api/desk', data=str(target))


class DeskTimer:
    def __init__(self, server):
        self.server = server
        self.timer = None

    def schedule(self, next_state):
        (delay, target) = next_state
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(
            delay.total_seconds(),
            DeskTimer.run,
            (self, target))
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.cancel()

    def run(self, target):
        go(self.server, target)

    def __repr__(self):
        return 'DeskTimer(server={}, timer={})'.format(
            self.server,
            self.timer)


def program(server):
    timer = DeskTimer(server)
    try:
        while True:
            cmd = input()
            if cmd == 'stop':
                timer.cancel()
                print('{} stopping timer'.format(datetime.now()))
            else:
                try:
                    [delay_str, target_str] = cmd.split(' ')
                    delay = timedelta(seconds=float(delay_str))
                    target = int(target_str)
                    print('{} next state is {} in {}s'.format(
                        datetime.now(), target, delay))
                    timer.schedule((delay, target))
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
