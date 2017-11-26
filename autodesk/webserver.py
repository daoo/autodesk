from autodesk.controller import Controller
from autodesk.hardware import Hardware
from autodesk.model import Database, session_from_int, desk_from_int
from autodesk.timer import Timer
from datetime import datetime, timedelta
import autodesk.stats as stats
import flask
import json
import os

app = flask.Flask(__name__)
app.config.update(dict(
    DELAY=15,
    PIN_DOWN=15,
    PIN_UP=13,
    PIN_LIGHT=16,
    LIMIT_DOWN=50,
    LIMIT_UP=10,
    DATABASE=('/tmp/autodesk.db'),
    TIMER_PATH=('/tmp/autodesk.timer')
))
app.config.from_envvar('AUTODESK_CONFIG', silent=True)


def get_database():
    if not hasattr(flask.g, 'sqlite_database'):
        flask.g.sqlite_database = Database(app.config['DATABASE'])
    return flask.g.sqlite_database


def get_hardware():
    if not hasattr(flask.g, 'hardware'):
        delay = app.config['DELAY']
        motor_pins = (app.config['PIN_DOWN'], app.config['PIN_UP'])
        light_pin = app.config['PIN_LIGHT']
        flask.g.hardware = Hardware(delay, motor_pins, light_pin)
        flask.g.hardware.init()
    return flask.g.hardware


def get_controller():
    limit = (
        timedelta(minutes=app.config['LIMIT_DOWN']),
        timedelta(minutes=app.config['LIMIT_UP']))
    return Controller(
        get_hardware(),
        limit,
        Timer(app.config['TIMER_PATH']),
        get_database())


@app.teardown_appcontext
def close_database(_):
    if hasattr(flask.g, 'sqlite_database'):
        flask.g.sqlite_database.close()


@app.teardown_appcontext
def close_hardware(_):
    if hasattr(flask.g, 'hardware'):
        flask.g.hardware.close()


@app.route('/api/session', methods=['GET', 'PUT'])
def route_api_session():
    if flask.request.method == 'PUT':
        get_controller().set_session(
            datetime.now(),
            session_from_int(int(flask.request.data)))
        return ''
    elif flask.request.method == 'GET':
        return get_database().get_session_spans(
            datetime.fromtimestamp(0),
            datetime.now()
        )[-1].data.test('0', '1')


@app.route('/api/desk', methods=['GET', 'PUT'])
def route_api_desk():
    if flask.request.method == 'PUT':
        if not get_controller().set_desk(
            datetime.now(),
            desk_from_int(int(flask.request.data))):
            flask.abort(403)
        return ''
    elif flask.request.method == 'GET':
        return get_database().get_desk_spans(
            datetime.fromtimestamp(0),
            datetime.now()
        )[-1].data.test('0', '1')


@app.route('/api/timer/update')
def route_api_timer_update():
    get_controller().update_timer(datetime.now())
    return ''


@app.route('/api/sessions.json')
def route_api_get_session():
    def format(hour, minute, value):
        return {
            'time': '{:0>2}:{:0>2}'.format(hour, minute),
            'value': str(value)
        }

    start = 7*60
    end = 19*60

    def trim_day(measurments):
        return measurments[start:end]

    def trim_week(measurments):
        return measurments[0:5]

    def decorate(measurments):
        index = 0
        for measurments in measurments:
            yield (index // 60, index % 60, measurments)
            index += 1

    daily_active_time = stats.compute_daily_active_time(
        get_database().get_session_spans(
            datetime.fromtimestamp(0),
            datetime.now()
        ))
    grouped = stats.group_into_days(daily_active_time)
    decorated = [list(decorate(group)) for group in grouped]
    trimmed = trim_week([trim_day(group) for group in decorated])

    formatted = [[format(*data) for data in group] for group in trimmed]

    return flask.Response(json.dumps(formatted), mimetype='text/json')


@app.route('/static/<path>')
def route_static(path):
    return flask.send_from_directory('static', path)


@app.route('/')
def route_index():
    beginning = datetime.fromtimestamp(0)
    now = datetime.now()
    session_spans = get_database().get_session_spans(beginning, now)
    session_state = session_spans[-1].data.test("inactive", "active")
    desk_spans = get_database().get_desk_spans(beginning, now)
    desk_state = desk_spans[-1].data.test("down", "up")
    active_time = stats.compute_active_time(session_spans, desk_spans)
    return flask.render_template(
            'index.html',
            session=session_state,
            desk=desk_state,
            active_time=active_time)
