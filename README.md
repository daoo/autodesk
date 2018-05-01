# AutoDesk

Automatic standing desk control using GPIO.

[![Build Status](https://travis-ci.org/daoo/autodesk.svg?branch=master)](https://travis-ci.org/daoo/autodesk)
[![CodeCov](https://codecov.io/gh/daoo/autodesk/branch/master/graph/badge.svg)](https://codecov.io/gh/daoo/autodesk)
[![Coverity](https://scan.coverity.com/projects/15538/badge.svg)](https://scan.coverity.com/projects/15538)
![License](https://img.shields.io/github/license/daoo/autodesk.svg)

## Design

The software is built around an aiohttp server. It runs on a device with GPIO
pins which it uses to control controls the desk and it maintains the current
state (and history) in a SQLite database. The server also maintains a timer
which fires when its time to change position.

The client observes the lock/unlock events of the used computer as an activity
indicator and passes these events on to the server. The server then uses
them to calculate when to raise or lower the desk.

## Hardware Wiring

The GPIO pins are wired up to control two electrical switches (relays,
transistors, opto-couplers or something with similar function). These
electrical switches are then connected in place of the up/down switch buttons
that are commonly used on the desk-control dongles. If your desk have some
more complicated control protocol, you have to use a different approach.

Two desks have been tested, one with
[8P8C](https://en.wikipedia.org/wiki/Modular_connector#8P8C) connector and one
with a [7-pin DIN](https://en.wikipedia.org/wiki/DIN_connector) connector.

### 8P8C jack (RJ45 or Ethernet)

For desk controllers that uses 8P8C connectors, you can use a regular (RJ45)
Ethernet cable and strip one end. The tested desk used the blue, brown and
white wires for up/down like this:

```
  blue <-> blue/white => up
  blue <-> brown      => down
```

### 7-pin DIN jack

For desk controllers that uses 7-pin DIN connectors you have to get your hands
a connector with cable that can be stripped and connected to the GPIO. The
tested desk used pins 1, 2 and 3 for up/down like this:

```
  1 <-> 2 => up
  1 <-> 3 => down
```

(numbering clockwise male connector):

```
     4
   3   5
  2     6
   1   7
```

## Software

There is two parts to get this running, client and server.

### Server

The server runs on a raspberry or directly on the same PC as the client if you have
for example a [Adafruit FT232H](https://learn.adafruit.com/adafruit-ft232h-breakout/overview).
In general it needs to be a computer with access to GPIO pins.

The server provides a HTTP API for manually controlling the desk, setting the
session state and also showing some nice statistics. The client must be able to
reach this API over HTTP for the entire system to function. If running the
server on a raspberry Pi it is recommended to use SSH for security.

### Client

The client can be any computer that can make HTTP requests, the tricky part is
hooking in to the lock/unlock events. Methods for both Linux and Windows have
been developed and used with great success.

#### Linux

On Linux, run the `logger.py` script to listen for lock/unlock events via DBus.
Supply it with the URL to the session API endpoint like this (`autodesk` is the
host name of the computer running the server):

    logger.py http://autodesk/api/session

The host name could be localhost if using the previously mentioned FT232H.

#### Windows

On Windows, use the task scheduler to setup tasks that sets the session state
with curl (`autodesk` is again the host name of the computer running the
server):

    curl -X PUT -d "0" http://autodesk/api/session
    curl -X PUT -d "1" http://autodesk/api/session
