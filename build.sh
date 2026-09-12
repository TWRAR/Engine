#!/usr/bin/env bash
set -euo pipefail

echo "Installing build dependencies..."
python -m pip install -r requirements.txt -q
python -m pip install pyinstaller -q

echo
python scripts/build_exe.py
