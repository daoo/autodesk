# AutoDesk

Automatic standing desk control using a Raspberry Pi.

[![Build Status](https://travis-ci.org/daoo/autodesk.svg?branch=master)](https://travis-ci.org/daoo/autodesk)
[![CodeCov](https://codecov.io/gh/daoo/autodesk/branch/master/graph/badge.svg)](https://codecov.io/gh/daoo/autodesk)
[![Coverity](https://scan.coverity.com/projects/15538/badge.svg)](https://scan.coverity.com/projects/15538)
![License](https://img.shields.io/github/license/daoo/autodesk.svg)

## Design

The software is built around a server `autodesk.server`. It runs on the Pi and
controls the desk motors via GPIO, maintains the current desk and session state
in a sqlite database, and also runs a timer that changes the desk state based
on the current active time.

The session logger monitors DBus and notifies the web server over HTTP (wrap it
with SSH for security) of session activation and inactivation (lock/unlock)
events.

## Usage

### Hardware

Setup your Raspberry Pi with two relays circuits (you could probably use
transistors directly as the voltage and current are usually pretty low for the
control switches). Then setup the cables and connector as needed depending on
what your desk controller uses.

#### 8P8C jack (AKA RJ45 or Ethernet)

Some desk controllers uses 8P8C connectors, i.e. you can use a regular (RJ45)
ethernet cable, see image below. One of those desks uses blue, brown and white
like this:

```
  blue <-> blue/white => up
  blue <-> brown      => down
```

![RJ45 connector with coloring](docs/8p8c.png)

#### 7-pin DIN jack

Other desk controllers uses 7-pin DIN connectors, see image below. One of those
desks uses pins 1, 2 and three like this:

```
  1 <-> 2 => up
  1 <-> 3 => down
```

![7-pin DIN jack with numbers](docs/7-pin-din.png)

### Server Software

Check out [install.sh](install.sh) for installation steps.

### Workstation Software

On Linux, run the `logger.py` script to listen for lock/unlock events via DBus.

    logger.py http://autodesk/api/session

On Windows, use the task scheduler to setup tasks that sets the session state
with curl and the HTTP API:

    curl -X PUT -d "0" http://autodesk/api/session
    curl -X PUT -d "1" http://autodesk/api/session

## TODO

* Configurable desk heights, now it justs goes up and down for 15 seconds which
  is the time it takes to reach bottom and up with my desk.
