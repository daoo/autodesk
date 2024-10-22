#!/usr/bin/env bash

curl \
  --data active \
  --header 'Content-Type: text/plain' \
  --request PUT \
  http://localhost:7380/api/session
