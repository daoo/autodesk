#!/usr/bin/env bash

set -eu

echo "Running ruff check..."
uv run ruff check bin src tests

echo "Running ty check..."
uv run ty check src tests
