#!/usr/bin/env bash

set -eu

pytest --cov=autodesk --cov-branch
ruff check autodesk tests
