# AutoDesk

Automatic standing desk control over GPIO.

[![Build Status](https://travis-ci.org/daoo/autodesk.svg?branch=master)](https://travis-ci.org/daoo/autodesk)
[![CodeCov](https://codecov.io/gh/daoo/autodesk/branch/master/graph/badge.svg)](https://codecov.io/gh/daoo/autodesk)
![License](https://img.shields.io/github/license/daoo/autodesk.svg)

## Design

The software is built around an aiohttp server. It runs on a device with GPIO
pins which it uses to control controls the desk and it maintains the current
state (and history) in a SQLite database. The server also maintains a timer
which fires when its time to change position.

The client observes the lock/unlock events of the used computer as an activity
indicator and passes these events on to the server. The server then uses
them to calculate when to raise or lower the desk.

## Connecting to the desk

The GPIO pins are wired up to control two electrical switches (relays,
transistors, opto-couplers or something with similar function). These
electrical switches are connected to the ports of the up/down buttons on the
desk's control dongle. If your desk use a more complicated control protocol,
you have to use a different approach.

Two desks have been tested, one with a
[8P8C](https://en.wikipedia.org/wiki/Modular_connector#8P8C) connector and one
with a [7-pin DIN](https://en.wikipedia.org/wiki/DIN_connector) connector.

### 8P8C jack (RJ45 or Ethernet)

For desk controllers that uses 8P8C connectors, you can use a regular (RJ45)
Ethernet cable and strip one end. The tested desk used the blue, brown and
white wires for up/down like this:

    blue <-> blue/white => up
    blue <-> brown      => down

### 7-pin DIN jack

For desk controllers that uses 7-pin DIN connectors you have to get your hands
a connector with cable that can be stripped and connected to the GPIO. The
tested desk used pins 1, 2 and 3 for up/down like this:

    1 <-> 2 => up
    1 <-> 3 => down

(numbering clockwise male connector):

       4
     3   5
    2     6
     1   7

## Hardware controller

Below is an example schematic connecting the digital GPIO pins of a FT232H (can
also use a Raspberry Pi) with the desk controller using two `4N35`
optocouplers. Additionally, the following features are included:

  * LED to indicate that the desk is moving,
  * LED to indicate the session state,
  * override buttons for manually adjusting desk height,
  * additional input button for software features.

<img src="schematic.svg" alt="autodesk controller schematic." width="1080" />

A PCB have been designed for the schematic above:

<img src="pcb.svg" alt="autodesk controller PCB." width="400" />

Schematic and PCB design created with EasyEDA and available here:
[easyeda.com/daoo/autodesk](https://easyeda.com/daoo/autodesk).

## Software

There is two parts to get this running, client and server.

### Server

The server runs on a raspberry or directly on the same PC as the client if you have
for example a [Adafruit FT232H](https://learn.adafruit.com/adafruit-ft232h-breakout/overview).
In general it needs to be a computer with access to GPIO pins.

A HTTP API for manually controlling the desk, setting the session state and
also showing some nice statistics. The client must be able to reach this API
over HTTP for the entire system to function. If running the server on a
raspberry Pi it is recommended to use SSH for security.

To interface with the FT232H the
[Adafruit_Python_GPIO](https://github.com/adafruit/Adafruit_Python_GPIO)
library is used and it must be installed manually from git as it is not up to
date in the python repository (as of 2019-08-16).

### Client

The client can be any computer that can make HTTP requests to set the session
state on the server. The tricky part is hooking in to the lock/unlock events.
On Linux a [pydbus](https://github.com/LEW21/pydbus) is used to listen to the
session activation events. On Windows the task scheduler can be set up to run
specific scripts on session activation events.

## Installation and setup

The program can be setup on a Windows or a Linux computer using the following
instructions.

### Linux

On Linux the installation is very straight forward.

#### Server

Make sure `libftdi` and its python library is installed using the
system package manager. For example, on Arch Linux:

    # pacman -S libftdi

Use the following commands to setup the server:

    $ cd ~/opt
    $ git clone https://github.com/daoo/autodesk
    $ git clone https://github.com/adafruit/Adafruit_Python_GPIO
    $ cd autodesk
    $ python -m venv --system-site-packages venv
    $ ./venv/bin/python -m pip install --upgrade pip setuptools
    $ ./venv/bin/pip install .
    $ ./venv/bin/pip install ../Adafruit_Python_GPIO
    $ ./bin/start-autodesk.sh

`--system-site-packages` is needed as libftdi is installed
system-wide and not part of the specific virtual env.

#### Client

On Linux, run the `logger.py` script to listen for lock/unlock events via DBus.
Supply it with the URL to the session API endpoint like this (`autodesk` is the
host name of the computer running the server):

    $ logger.py http://autodesk/api/session

The host name could be localhost if using the previously mentioned FT232H.

### Windows

On Windows, many extra steps are needed to set the right USB driver and
to install libftdi.

#### Server

Use the following commands to setup the server:

    $ cd ~/opt
    $ git clone https://github.com/daoo/autodesk
    $ git clone https://github.com/adafruit/Adafruit_Python_GPIO
    $ cd autodesk
    $ python -m venv venv
    $ ./venv/Scripts/python -m pip install --upgrade pip setuptools
    $ ./venv/Scripts/pip install .
    $ ./venv/Scripts/pip install ../Adafruit_Python_GPIO

Before running the autodesk server the USB driver needs to be configured and
libftdi needs to be installed into the virtual environment.

#### FT23H2 Zadig

Download [Zadig](http://zadig.akeo.ie/) and use it to change the driver to
`libusbK` for the FT232H device. See [Adafruit's
guide](https://learn.adafruit.com/adafruit-ft232h-breakout/windows-setup) for
more information.

#### Build and install libftdi

Use [msys2](https://www.msys2.org/) to build and install libftdi. Make sure to
use MinGW 64 bit with Python 3 installed in Windows. To start msys2 MinGW 64
with PATH imported from Windows, run the following command:

    msys2_shell.cmd -use-full-path -mingw64

The default cmake script does not work with Python 3 in Windows. There is a
modified script available in the `python3` branch at
[daoo/libftdi](https://github.com/daoo/libftdi) together with a custom install
script `install-into-venv.sh`.

To build libftdi in the launched shell:

    $ pacman -S mingw-w64-x86_64-cmake \
          mingw-w64-x86_64-confuse mingw-w64-x86_64-libusb mingw-w64-x86_64-swig \
          mingw-w64-x86_64-boost mingw-w64-x86_64-toolchain
    $ pacman -Rsc mingw-w64-x86_64-python3
    $ which cmake # ensure this is mingw64
    $ cd ~/opt
    $ git clone https://github.com/daoo/libftdi
    $ cd libftdi
    $ git checkout python3
    $ mkdir build
    $ cd build
    $ cmake -G "MSYS Makefiles" ..
    $ make
    $ install-into-venv.sh /c/Users/USER/opt/autodesk/venv

Now the autodesk server can be started back in the Windows shell:

    $ ./bin/start-autodesk.ps1

#### Client

Use the Windows task scheduler to setup tasks that sets the session state using
the `bin/autodesk-activate.ps1` and `bin/autodesk-deactivate.ps1` scripts.
