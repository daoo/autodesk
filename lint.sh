#!/usr/bin/env bash

set -eu

pycodestyle autodesk bin tests
pyflakes autodesk bin tests
