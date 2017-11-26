#!/usr/bin/env bash

# Assuming running as root on Arch Linux

set -e

pacman -S --needed apache openssl nginx gcc python-setuptools python-virtualenv sudo git nanomsg sqlite

id -u autodesk &>/dev/null || \
  sudo useradd -d /var/local/autodesk -m -r -s /usr/bin/nologin autodesk

cd /var/local/autodesk
sudo -u autodesk git clone https://github.com/daoo/autodesk.git

sudo -u autodesk virtualenv venv
sudo -u autodesk venv/bin/pip install ./autodesk uwsgi

sudo -u autodesk mkfifo timer

cp autodesk/sys/nginx.conf /etc/nginx/nginx.conf
cp autodesk/sys/autodesk-{server,uwsgi}.service /etc/systemd/system

sudo -u autodesk mkdir -p certs
sudo -u autodesk openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout certs/autodesk.key -out certs/autodesk.crt
sudo -u autodesk openssl dhparam -out certs/dhparam.pem 4096

echo "Input admin password:"
sudo -u autodesk htpasswd -c htpasswd admin

sudo -u autodesk tee settings.cfg <<HERE
DELAY = 15
PIN_DOWN = 15
PIN_UP = 13
PIN_LIGHT = 16
LIMIT_DOWN = 50
LIMIT_UP = 10
DATABASE = '/var/local/autodesk/desk.db'
TIMER_PATH = '/var/local/autodesk/timer'
HERE

systemctl enable --now autodesk-{uwsgi,timer}.service nginx.service
