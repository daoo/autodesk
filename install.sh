#!/usr/bin/env bash

# Assuming running as root on Arch Linux

set -e

pacman -S --needed gcc python-setuptools python-virtualenv sudo git sqlite

id -u autodesk &>/dev/null || \
  sudo useradd -d /var/local/autodesk -m -r -s /usr/bin/nologin autodesk

cd /var/local/autodesk
[[ -d autodesk/.git ]] || \
  sudo -u autodesk git clone https://github.com/daoo/autodesk.git

[[ -d venv ]] || \
  sudo -u autodesk virtualenv venv
sudo -u autodesk venv/bin/pip install ./autodesk uwsgi

# TODO: install gpio libs
# sudo -u autodesk venv/bin/pip install RPi.GPIO
# sudo -u autodesk venv/bin/pip install Adafruit_GPIO FT232H

sudo -u autodesk ln -fsn autodesk/srv srv
sudo -u autodesk cp autodesk/sys/default.yml config.yml

cp autodesk/sys/autodesk.service /etc/systemd/system
cp autodesk/sys/99-gpio.rules /etc/udev/rules.d

systemctl enable --now autodesk.service
