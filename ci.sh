#!/usr/bin/env bash

set -eu

source ./.venv/bin/activate

pytest --cov=autodesk --cov-branch
ruff check autodesk tests
