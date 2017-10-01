#!/usr/bin/env python

from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import requests
import sys
import threading


class Server:
    def __init__(self, url, password):
        self.url = url
        self.auth = HTTPBasicAuth('admin', password)

    def set_desk(self, target):
        requests.put(self.url + '/api/desk', data=str(target), auth=self.auth)

    def update_timer(self):
        requests.get(self.url + '/api/timer/update', auth=self.auth)


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
        self.server.set_desk(target)


def program(server):
    timer = DeskTimer(server)

    try:
        server.update_timer()
    except requests.exceptions.ConnectionError:
        # Timer service started first, let
        # webserver update us when it starts.
        pass

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
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: {} CONFIG SERVER\n".format(sys.argv[0]))
        sys.exit(1)
    else:
        password = None
        with open(sys.argv[1], 'r') as file:
            for line in file:
                if line.startswith('PASSWORD'):
                    password = line[line.index('\'')+1:line.rindex('\'')]

        if not password:
            sys.stderr.write('Error: no password found\n')
            sys.exit(1)

        program(Server(sys.argv[2], password))

if __name__ == '__main__':
    main()
