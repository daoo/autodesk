#!/usr/bin/env bash

export AUTODESK_ADDRESS="127.0.0.1"
export AUTODESK_PORT="8080"
export AUTODESK_CONFIG="./config/ft232h.yml"
export AUTODESK_DATABASE="~/.local/share/autodesk/autodesk.db"

source ./.venv/bin/activate

python -m autodesk.program
