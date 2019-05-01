#!/usr/bin/env bash

set -eux

pytest
pycodestyle autodesk bin tests
pyflakes autodesk bin tests
