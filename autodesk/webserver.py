from autodesk.controller import Controller
from autodesk.hardware import Hardware
from autodesk.model import Database, session_from_int, desk_from_int
from autodesk.stats import Stats
from autodesk.timer import Timer
from datetime import datetime, timedelta
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
    start = 7*60
    end = 19*60

    def get_day(index, buckets):
        length = 24*60
        return buckets[index*length:(index+1)*length]

    def split_days(buckets):
        yield get_day(0, buckets)
        yield get_day(1, buckets)
        yield get_day(2, buckets)
        yield get_day(3, buckets)
        yield get_day(4, buckets)
        yield get_day(5, buckets)
        yield get_day(6, buckets)

    def format_time(hour, minute, value):
        return {
            'time': '{:0>2}:{:0>2}'.format(hour, minute),
            'value': str(value)
        }

    def format_day(minutes):
        index = start
        for value in minutes:
            hour = index // 60
            minute = index % 60
            yield format_time(hour, minute, value)
            index += 1

    def cut(day):
        return day[start:end]

    stats = Stats(get_database())
    result = stats.compute_daily_active_time(
        datetime.fromtimestamp(0),
        datetime.now()
    )

    return flask.Response(
        json.dumps([list(format_day(cut(day))) for day in split_days(result)]),
        mimetype='text/json')


@app.route('/static/<path>')
def route_static(path):
    return flask.send_from_directory('static', path)


@app.route('/')
def route_index():
    return flask.render_template(
        'index.html',
        active_time=get_database().get_snapshot(
            datetime.fromtimestamp(0),
            datetime.now()).get_active_time())
