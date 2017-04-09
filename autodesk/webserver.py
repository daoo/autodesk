from autodesk.controller import Controller
from autodesk.hardware import Hardware
from autodesk.timer import Timer
from datetime import datetime, timedelta
from autodesk.model import Database, session_from_int, desk_from_int
import flask
import os

app = flask.Flask(__name__)
app.config.update(dict(
    DELAY=15,
    PIN_DOWN=15,
    PIN_UP=13,
    LIMIT_DOWN=50,
    LIMIT_UP=10,
    DATABASE=os.path.join(app.root_path, 'autodesk.db'),
    TIMER_PATH=os.path.join(app.root_path, 'timer')
))
app.config.from_envvar('AUTODESK_CONFIG', silent=True)


def get_db():
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = Database(app.config['DATABASE'])
    return flask.g.sqlite_db


def get_controller():
    delay = app.config['DELAY']
    pins = (app.config['PIN_DOWN'], app.config['PIN_UP'])
    limit = (
        timedelta(minutes=app.config['LIMIT_DOWN']),
        timedelta(minutes=app.config['LIMIT_UP']))
    return Controller(Hardware(delay, pins), limit, Timer(app.config['TIMER_PATH']), get_db())


@app.teardown_appcontext
def close_db(_):
    if hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db.close()


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


@app.route('/')
def route_index():
    return flask.render_template(
        'index.html',
        active_time=get_db().get_snapshot(
            datetime.fromtimestamp(0),
            datetime.now()).get_active_time())
