#!/usr/bin/env bash

uv run pytest --cov=src --cov-branch --cov-report=term --cov-report=json tests
