#!/usr/bin/env bash

set -eu

source ./.venv/bin/activate

pytest --cov=autodesk --cov-branch --cov-report=term --cov-report=json
ruff check autodesk tests
