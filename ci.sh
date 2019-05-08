#!/usr/bin/env bash

set -eux

pytest --cov=autodesk --cov-branch
pycodestyle autodesk bin tests
pyflakes autodesk bin tests
