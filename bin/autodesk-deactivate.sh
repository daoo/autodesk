#!/usr/bin/env bash

curl.exe \
  --data 0 \
  --header 'Content-Type: text/plain' \
  --request PUT \
  http://localhost:8080/api/session
