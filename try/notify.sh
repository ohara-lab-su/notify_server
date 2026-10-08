#!/usr/bin/env bash

# NOTIFY_SERVER_URL and NOTIFY_TOKEN are supplied as environment variables.
# Notification failure never changes the calculation command's exit status.

if ./run_calc.sh; then
    python -c 'from notify import notify; notify("OK", "Calculation finished successfully.")'
else
    status=$?
    python -c 'from notify import notify; notify("FAILED", "Calculation failed.")'
    exit "$status"
fi
