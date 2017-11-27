from autodesk.model import Database
from datetime import datetime
from nanomsg import Socket, PUSH
import autodesk.stats as stats
import flask
import json
import msgpack

app = flask.Flask(__name__)
app.config.update(dict(
    SERVER_ADDRESS='tcp://127.0.0.1:12345',
    DATABASE='/tmp/autodesk.db',
))
app.config.from_envvar('AUTODESK_CONFIG', silent=True)


def get_database():
    if not hasattr(flask.g, 'database'):
        flask.g.database = Database(app.config['DATABASE'])
    return flask.g.database


def get_socket():
    if not hasattr(flask.g, 'socket'):
        flask.g.socket = Socket(PUSH)
        flask.g.socket.connect(app.config['SERVER_ADDRESS'])
    return flask.g.socket


@app.teardown_appcontext
def close_database(_):
    if hasattr(flask.g, 'database'):
        flask.g.database.close()


@app.teardown_appcontext
def close_socket(_):
    if hasattr(flask.g, 'database'):
        flask.g.database.close()


@app.route('/api/session', methods=['GET', 'PUT'])
def route_api_session():
    if flask.request.method == 'PUT':
        get_socket().send(msgpack.packb([
            'session',
            int(flask.request.data)
        ]))
        return ''
    elif flask.request.method == 'GET':
        return get_database().get_session_spans(
            datetime.fromtimestamp(0),
            datetime.now()
        )[-1].data.test('0', '1')


@app.route('/api/desk', methods=['GET', 'PUT'])
def route_api_desk():
    if flask.request.method == 'PUT':
        get_socket().send(msgpack.packb([
            'desk',
            int(flask.request.data)
        ]))
        return ''
    elif flask.request.method == 'GET':
        return get_database().get_desk_spans(
            datetime.fromtimestamp(0),
            datetime.now()
        )[-1].data.test('0', '1')


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
