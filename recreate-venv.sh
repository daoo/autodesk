#!/usr/bin/env bash

set -ue

if [[ -n "${VIRTUAL_ENV+}" ]]; then
  echo "Error: venv active, please deactivate first."
  exit 1
fi
rm -rf "./venv/"
python -m venv "./venv"
./venv/bin/pip install --upgrade pip setuptools
./venv/bin/pip install \
  -r requirements.txt \
  -r requirements-ci.txt \
  -r requirements-dev.txt
