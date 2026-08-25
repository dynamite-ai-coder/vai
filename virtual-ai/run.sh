#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "Starting Virtual AI on http://127.0.0.1:22200"
echo "Press Ctrl+C to stop"
echo ""

python main.py
