#!/usr/bin/env bash

set -eux

pytest --cov=autodesk --cov-branch tests
pycodestyle autodesk bin tests
pyflakes autodesk bin tests
