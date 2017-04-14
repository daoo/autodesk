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


def get_controller():
    delay = app.config['DELAY']
    pins = (app.config['PIN_DOWN'], app.config['PIN_UP'])
    limit = (
        timedelta(minutes=app.config['LIMIT_DOWN']),
        timedelta(minutes=app.config['LIMIT_UP']))
    return Controller(
        Hardware(delay, pins),
        limit,
        Timer(app.config['TIMER_PATH']),
        get_database())


@app.teardown_appcontext
def close_database(_):
    if hasattr(flask.g, 'sqlite_database'):
        flask.g.sqlite_database.close()


@app.route('/api/set/session/<string>')
def route_api_set_session(string):
    get_controller().set_session(
        datetime.now(),
        session_from_int(int(string)))
    return ''


@app.route('/api/set/desk/<string>')
def route_api_set_desk(string):
    state = desk_from_int(int(string))
    if not get_controller().set_desk(datetime.now(), state):
        flask.abort(403)
    return ''


@app.route('/api/get/session.json')
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
    desk_spans = get_database().get_desk_spans(beginning, now)
    active_time = stats.compute_active_time(session_spans, desk_spans)
    return flask.render_template('index.html', active_time=active_time)
