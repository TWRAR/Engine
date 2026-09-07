#!/usr/bin/env bash
set -euo pipefail

echo "Installing build dependencies..."
python -m pip install -e ".[build]" -q

echo
python scripts/build_exe.py
