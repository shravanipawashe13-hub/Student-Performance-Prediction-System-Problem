#!/usr/bin/env bash
# Universal Linux / macOS Runner for Student Performance Prediction System
cd "$(dirname "$0")"

echo "======================================================================"
echo "   Student Performance Prediction System (BCA Academic Project)"
echo "======================================================================"

# Detect Python 3
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3 was not found. Please install Python 3.9+."
    exit 1
fi

echo "[INFO] Detected Python: $($PY_CMD --version)"

# Execute master runner
$PY_CMD run.py
