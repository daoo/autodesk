#!/usr/bin/env bash

export AUTODESK_ADDRESS="127.0.0.1"
export AUTODESK_PORT="7380"
export AUTODESK_CONFIG="./config/ft232h.yml"
export AUTODESK_DATABASE="$HOME/AppData/Local/autodesk/autodesk.db"

uv run autodesk
