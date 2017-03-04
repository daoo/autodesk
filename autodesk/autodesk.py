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
    if string == str(model.SESSION_ACTIVE):
        get_controller().set_session(
            model.SESSION_ACTIVE, datetime.now())
    elif string == str(model.SESSION_INACTIVE):
        get_controller().set_session(
            model.SESSION_INACTIVE, datetime.now())
    else:
        flask.abort(400)
    return ''


@app.route('/api/set/desk/<string>')
def route_api_set_desk(string):
    if string == str(model.STATE_DOWN):
        state = model.STATE_DOWN
    elif string == str(model.STATE_UP):
        state = model.STATE_UP
    else:
        flask.abort(400)

    if not get_controller().set_desk(state, datetime.now()):
        flask.abort(403)

    return ''


@app.route('/')
def route_index():
    return flask.render_template(
        'index.html',
        active_time=get_db().get_snapshot(
            datetime.fromtimestamp(0),
            datetime.now()).get_active_time())
