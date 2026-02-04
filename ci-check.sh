#!/usr/bin/env bash

uv run ruff check bin src tests
uv run ty check src tests
