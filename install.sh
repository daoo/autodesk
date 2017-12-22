#!/usr/bin/env bash

# Assuming running as root on Arch Linux

set -e

pacman -S --needed gcc python-setuptools python-virtualenv sudo git sqlite

id -u autodesk &>/dev/null || \
  sudo useradd -d /var/local/autodesk -m -r -s /usr/bin/nologin autodesk

cd /var/local/autodesk
sudo -u autodesk git clone https://github.com/daoo/autodesk.git

sudo -u autodesk virtualenv venv
sudo -u autodesk venv/bin/pip install ./autodesk uwsgi

cp autodesk/sys/autodesk.service /etc/systemd/system

sudo -u autodesk cp sys/default.yml config.yml

systemctl enable --now autodesk.service
