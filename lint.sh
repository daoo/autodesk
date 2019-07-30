#!/usr/bin/env bash

set -eu

exitcode=0
pycodestyle --ignore=E306,W503 autodesk bin tests || exitcode=1
pyflakes autodesk bin tests || exitcode=1

exit $exitcode
