#!/bin/sh
# Start the private loopback sandbox. Does not print the access secret.
set -eu
cd "$(dirname "$0")"
exec python3 server.py
