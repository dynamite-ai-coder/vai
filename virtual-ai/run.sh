#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "========================================="
echo "  VIRTUAL AI - Multi-Model Intelligence"
echo "========================================="
echo ""
echo "Models configured:"
echo "  1. Reasoning: deepseek-r1-distill-llama-70b"
echo "  2. Research: llama-3.3-70b-versatile"
echo "  3. Critical: mixtral-8x7b-32768"
echo "  4. Engineering: llama-3.1-8b-instant"
echo "  5. Strategy: gemma2-9b-it"
echo ""
echo "Starting server on http://127.0.0.1:22200"
echo "Press Ctrl+C to stop"
echo ""

python main.py
