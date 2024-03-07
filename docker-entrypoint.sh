#!/bin/bash
set -e
if [ "$RUN_MODE_ENV" = "API" ]; then
    exec hypercorn api.api:app -b 0.0.0.0:80 --worker-class trio
else
    exec python main.py "$@"
fi
