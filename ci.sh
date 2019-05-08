#!/usr/bin/env bash

set -eu

pytest --cov=autodesk --cov-branch
./lint.sh
