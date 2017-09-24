# AutoDesk

Automatic standing desk control using a Raspberry Pi.

## Design

The software consists of three components:

  * Session logger
  * Web server
  * Timer server

The web and timer servers run on the Pi and the session logger runs on the
workstation.

The session logger monitors DBus and notifies the web server over HTTP (wrap it
with SSH for security) of session activation and inactivation (lock/unlock)
events.

The web server maintains a database (SQLite) of desk (up/down) and session
(active/inactive) events. Every time an event occurs, the active time is
computed for the current desk state (that is how long have I been sitting or
standing). This time is compared against a fixed limit and the timer server is
notified about when the desk state should be changed next. The web server also
provides an API for manually forcing the desk to a desired state.

The timer server is communicated to over a named pipe with a dumb text
protocol. It maintains a timer (fixed delay) and what the next state should be.
The timer can be stopped and updated (shorter/longer delay or different next
state).

## Usage

### Hardware

Setup your Raspberry Pi with some relays (you probably need two relays).

The desk used in my setup connects control dongles via regular Ethernet cables.
Blue, brown and white are used for up and down like this:

  * Blue to blue/white is up.
  * Blue to brown is down.

### Software

Setup a virtualenv and install autodesk:

    virtualenv /var/local/autodesk/venv
    /var/local/autodesk/venv/bin/pip install ./autodesk

Add a configuration in `/var/local/autodesk/settings.cfg` (pins are in
`GPIO.BOARD` mode, limit times are in minutes):

    DELAY = 15
    PIN_DOWN = 15
    PIN_UP = 13
    LIMIT_DOWN = 50
    LIMIT_UP = 10
    DATABASE = '/var/local/autodesk/desk.db'
    TIMER_PATH = '/var/local/autodesk/timer'

Run the flask app (use whatever port you like):

    AUTODESK_CONFIG=/var/local/autodesk/settings.cfg FLASK_APP=autodesk.webserver flask run -p 8000

Also, start the timer server like this:

    tail -n1 -f /var/local/autodesk/timer | autodesk-timer http://localhost:8000

Finally, install `logger.py` on your workstation, setup a SSH tunnel (if using,
here local port 8000 is tunneled to the Pi) and run the logger like this:

    logger.py http://localhost:8000/api/set/session

It prints what DBus sessions it will monitor when starting.

## TODO

* Configurable desk heights, now it justs goes up and down for 15 seconds which
  is the time it takes to reach bottom and up with my desk.
