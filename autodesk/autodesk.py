from autodesk.controller import Controller
from datetime import datetime
import autodesk.model as model
import flask
import os

app = flask.Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'autodesk.db'),
    TIMER_PATH=os.path.join(app.root_path, 'timer')
))
app.config.from_envvar('AUTODESK_CONFIG', silent=True)


def get_db():
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = model.Database(app.config['DATABASE'])
    return flask.g.sqlite_db


def get_controller():
    return Controller(app.config['TIMER_PATH'], get_db())


@app.teardown_appcontext
def close_db(_):
    if hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db.close()


@app.route('/api/set/session/<string>')
def route_api_set_session(string):
    try:
        get_controller().set_session(
            datetime.now(),
            model.session_from_int(int(string)))
        return ''
    except Exception as e:
        flask.abort(400)


@app.route('/api/set/desk/<string>')
def route_api_set_desk(string):
    try:
        state = model.desk_from_int(int(string))
        if not get_controller().set_desk(datetime.now(), state):
            flask.abort(403)
        return ''
    except:
        flask.abort(400)


@app.route('/')
def route_index():
    return flask.render_template(
        'index.html',
        active_time=get_db().get_snapshot(
            datetime.fromtimestamp(0),
            datetime.now()).get_active_time())