#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PID=$(lsof -ti:22200 2>/dev/null || true)

if [ -n "$PID" ]; then
    echo "Stopping Virtual AI (PID: $PID)..."
    kill "$PID" 2>/dev/null
    sleep 1
    kill -9 "$PID" 2>/dev/null || true
    echo "Stopped."
else
    echo "Virtual AI is not running on port 22200."
fi
