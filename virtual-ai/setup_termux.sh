#!/bin/bash
set -e

echo "========================================="
echo "  VIRTUAL AI - Termux Setup"
echo "========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "[ERROR] Python not found. Install with: pkg install python"
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1)
echo "[OK] $PY_VERSION"

if ! command -v pip3 &>/dev/null && ! command -v pip &>/dev/null; then
    echo "[ERROR] pip not found. Install with: pkg install python-pip"
    exit 1
fi
echo "[OK] pip found"

if [ ! -d ".venv" ]; then
    echo "[...] Creating virtual environment..."
    $PYTHON -m venv .venv
    echo "[OK] Virtual environment created"
fi

echo "[...] Activating virtual environment..."
source .venv/bin/activate

echo "[...] Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "[OK] Dependencies installed"

echo "[...] Setting up optional dependencies..."
pip install browser-use --quiet 2>/dev/null || echo "[WARN] browser-use optional - will use fallback"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "[WARN] Created .env from example - please edit it with your API keys"
else
    echo "[OK] .env file exists"
fi

mkdir -p static
chmod +x run.sh stop.sh

echo ""
echo "========================================="
echo "  SETUP COMPLETE"
echo "========================================="
echo ""
echo "1. Edit .env with your 5 Groq API keys"
echo "   Each model uses a different API key"
echo "   Models: deepseek-r1, llama-3.3, mixtral, llama-3.1, gemma2"
echo ""
echo "2. Run: ./run.sh"
echo "3. Open: http://127.0.0.1:22200"
echo ""
