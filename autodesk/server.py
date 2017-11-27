from autodesk.controller import Controller
from autodesk.hardware import Hardware
from autodesk.model import Database, desk_from_int, session_from_int
from autodesk.timer import Timer
from datetime import datetime, timedelta
from nanomsg import Socket, PULL
import msgpack
import os
import sys


def server(address, controller):
    with Socket(PULL) as socket:
        socket.bind(address)

        while True:
            try:
                msg = msgpack.unpackb(socket.recv())
                if msg[0] == b'stop':
                    break
                elif msg[0] == b'desk':
                    controller.set_desk(
                        datetime.now(), desk_from_int(msg[1]))
                elif msg[0] == b'session':
                    controller.set_session(
                        datetime.now(), session_from_int(msg[1]))
                else:
                    sys.stderr.write(
                        "Error: unknown message \"{}\"\n".format(msg))
            except KeyboardInterrupt:
                break
            except Exception as e:
                sys.stderr.write(repr(e) + '\n')


def send_desk_msg(address, target):
    with Socket(PUSH) as socket:
        socket.connect(address)
        socket.send(message.packb(['desk', target.test(0, 1)]))


class Args:
    def __init__(self, envs):
        self.database = envs.get('AUTODESK_DATABASE', '/tmp/autodesk.db')
        self.delay = int(envs.get('AUTODESK_DELAY', '15'))
        self.pin_down = int(envs.get('AUTODESK_PIN_DOWN', '15'))
        self.pin_up = int(envs.get('AUTODESK_PIN_UP', '13'))
        self.pin_light = int(envs.get('AUTODESK_PIN_LIGHT', '16'))
        self.limit_down = int(envs.get('AUTODESK_LIMIT_DOWN', '50'))
        self.limit_up = int(envs.get('AUTODESK_LIMIT_UP', '10'))
        self.server_address = envs.get('AUTODESK_SERVER_ADDRESS',
                                       'tcp://127.0.0.1:12345')


def start(args):
    database = Database(args.database)
    hardware = Hardware(
        args.delay,
        (args.pin_down, args.pin_up),
        args.pin_light)
    limit = (
        timedelta(minutes=args.limit_down),
        timedelta(minutes=args.limit_up))
    timer = Timer(lambda target: send_desk_msg(args.server_address, target))
    controller = Controller(hardware, limit, timer, database)
    hardware.init()
    controller.init(datetime.now())
    server(args.server_address, controller)
    controller.close()
    hardware.close()
    database.close()


start(Args(os.environ))
