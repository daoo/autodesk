#!/usr/bin/env bash

# Assuming running as root

set -e

pacman -S --needed apache openssl nginx gcc python-setuptools python-virtualenv sudo git nanomsg sqlite

id -u autodesk &>/dev/null || \
  sudo useradd -d /var/local/autodesk -m -r -s /usr/bin/nologin autodesk

cd /var/local/autodesk
sudo -u autodesk git clone https://github.com/daoo/autodesk.git

sudo -u autodesk virtualenv venv
sudo -u autodesk venv/bin/pip install ./autodesk uwsgi

cp autodesk/sys/nginx.conf /etc/nginx/nginx.conf
cp autodesk/sys/autodesk-{server,uwsgi}.service /etc/systemd/system

sudo -u autodesk mkdir -p certs
sudo -u autodesk openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout certs/autodesk.key -out certs/autodesk.crt
sudo -u autodesk openssl dhparam -out certs/dhparam.pem 4096

echo "Input admin password:"
sudo -u autodesk htpasswd -c htpasswd admin

sudo -u autodesk tee server.cfg <<HERE
AUTODESK_DELAY=15
AUTODESK_PIN_DOWN=15
AUTODESK_PIN_UP=13
AUTODESK_PIN_LIGHT=16
AUTODESK_LIMIT_DOWN=50
AUTODESK_LIMIT_UP=10
AUTODESK_DATABASE=/var/local/autodesk/desk.db
AUTODESK_SERVER_ADDRESS=tcp://127.0.0.1:12345
HERE

sudo -u autodesk tee flask.cfg <<HERE
DATABASE="/var/local/autodesk/desk.db"
SERVER_ADDRESS="tcp://127.0.0.1:12345"
HERE

systemctl enable --now autodesk-{uwsgi,server}.service nginx.service
