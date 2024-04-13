#!/usr/bin/env bash

set -ue

if [[ -n "${VIRTUAL_ENV+}" ]]; then
  echo "Error: venv active, please deactivate first."
  exit 1
fi

rm -rf "./venv/"
uv venv venv

source ./venv/bin/activate
uv pip install -r requirements.txt -r requirements-ci.txt -r requirements-dev.txt
